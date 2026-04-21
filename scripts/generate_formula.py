#!/usr/bin/env python3
"""
Generate a Homebrew formula for zev by fetching metadata from PyPI
and running homebrew-pypi-poet to collect dependency resources.

Usage:
    pip install homebrew-pypi-poet
    pip install zev==<version>
    python scripts/generate_formula.py <version>
"""

import json
import re
import subprocess
import sys
import urllib.request


# Packages that require native compilation (Rust/C) — use binary wheels to avoid toolchain deps.
NATIVE_PACKAGES = {"jiter", "pydantic-core"}
ARM64_TAG = "macosx_11_0_arm64"
X86_64_TAG = "macosx_10_12_x86_64"


def get_pypi_tarball(version: str) -> tuple[str, str]:
    url = f"https://pypi.org/pypi/zev/{version}/json"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    for f in data["urls"]:
        if f["filename"].endswith(".tar.gz"):
            return f["url"], f["digests"]["sha256"]
    raise RuntimeError(f"No source tarball found for zev {version}")


def get_wheel_urls(package: str, version: str) -> dict[str, tuple[str, str]]:
    """Return {platform_tag: (url, sha256)} for cp312 macOS wheels of a package."""
    url = f"https://pypi.org/pypi/{package}/{version}/json"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    result: dict[str, tuple[str, str]] = {}
    for f in data["urls"]:
        fn = f["filename"]
        if not fn.endswith(".whl") or "cp312" not in fn:
            continue
        for tag in (ARM64_TAG, X86_64_TAG):
            if tag in fn:
                result[tag] = (f["url"], f["digests"]["sha256"])
    return result


def parse_poet_output(output: str) -> list[dict]:
    """Parse poet stdout into a list of resource dicts with normalized (0-indent) block text."""
    resources = []
    lines = output.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r'(\s*)resource "([^"]+)" do\s*$', lines[i])
        if m:
            leading = m.group(1)
            name = m.group(2)
            block_lines: list[str] = []
            while i < len(lines):
                line = lines[i]
                # Strip the common leading indent introduced by poet
                normalized = line[len(leading):] if line.startswith(leading) else line.lstrip()
                block_lines.append(normalized)
                if line.strip() == "end":
                    i += 1
                    break
                i += 1
            block_str = "\n".join(block_lines)
            url_m = re.search(r'url "([^"]+)"', block_str)
            url = url_m.group(1) if url_m else ""
            ver_m = re.search(r'[/_-](\d+\.\d+[\d.]*)(?:\.tar\.gz|[-_.])', url)
            version = ver_m.group(1) if ver_m else ""
            resources.append({"name": name, "url": url, "version": version, "block": block_str})
        else:
            i += 1
    return resources


def get_poet_resources() -> str:
    result = subprocess.run(
        [sys.executable, "-m", "poet", "zev"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"poet failed: {result.stderr}")

    all_resources = parse_poet_output(result.stdout)
    # Drop the zev package itself
    all_resources = [r for r in all_resources if r["name"] != "zev"]

    native = [r for r in all_resources if r["name"] in NATIVE_PACKAGES]
    pure_python = [r for r in all_resources if r["name"] not in NATIVE_PACKAGES]

    sections: list[str] = []

    if native:
        # Fetch binary wheel URLs once per native package
        wheel_cache: dict[str, dict[str, tuple[str, str]]] = {}
        for res in native:
            wheel_cache[res["name"]] = get_wheel_urls(res["name"], res["version"])

        def make_arch_block(arch_name: str, platform_tag: str) -> str:
            lines = [f"on_{arch_name} do"]
            for i, res in enumerate(native):
                wheels = wheel_cache[res["name"]]
                if platform_tag not in wheels:
                    raise RuntimeError(
                        f"No cp312 wheel for {res['name']} {res['version']} on {platform_tag}"
                    )
                whl_url, whl_sha = wheels[platform_tag]
                lines.append(f'  resource "{res["name"]}" do')
                lines.append(f'    url "{whl_url}"')
                lines.append(f'    sha256 "{whl_sha}"')
                lines.append("  end")
                if i < len(native) - 1:
                    lines.append("")
            lines.append("end")
            return "\n".join(lines)

        sections.append(make_arch_block("arm", ARM64_TAG))
        sections.append(make_arch_block("intel", X86_64_TAG))

    for res in pure_python:
        sections.append(res["block"])

    while sections and not sections[0].strip():
        sections.pop(0)
    while sections and not sections[-1].strip():
        sections.pop()

    return "\n\n".join(sections)


def indent(text: str, spaces: int = 2) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())


def generate(version: str) -> str:
    tarball_url, sha256 = get_pypi_tarball(version)
    resources = get_poet_resources()

    return f"""\
class Zev < Formula
  include Language::Python::Virtualenv

  desc "Lookup CLI commands easily using AI"
  homepage "https://github.com/dtnewman/zev"
  url "{tarball_url}"
  sha256 "{sha256}"
  license "MIT"

  depends_on "python@3.12"

{indent(resources)}

  def install_resource(venv, resource)
    if resource.url&.end_with?(".whl")
      wheel_dir = buildpath/"homebrew-wheels"
      wheel_dir.mkpath
      wheel_name = resource.url.to_s.split("/").last
      wheel_path = wheel_dir/wheel_name
      FileUtils.cp(resource.cached_download, wheel_path)
      system "python3.12", "-m", "pip", "--python=#{{venv.root}}/bin/python", "install",
             "--verbose", "--no-deps", "--ignore-installed", "--no-compile", wheel_path
    else
      venv.pip_install resource
    end
  end

  def install
    venv = virtualenv_create(libexec, "python3.12")
    resources.each {{ |r| install_resource(venv, r) }}
    venv.pip_install_and_link buildpath
  end

  test do
    (testpath/".zevrc").write("LLM_PROVIDER=openai\\nOPENAI_API_KEY=test\\n")
    output = shell_output("HOME=\#{{testpath}} \#{{bin}}/zev --version")
    assert_match "zev version", output
  end
end
"""


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <version>", file=sys.stderr)
        sys.exit(1)
    print(generate(sys.argv[1]))
