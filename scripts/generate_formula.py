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
import subprocess
import sys
import urllib.request


def get_pypi_tarball(version: str) -> tuple[str, str]:
    url = f"https://pypi.org/pypi/zev/{version}/json"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    for f in data["urls"]:
        if f["filename"].endswith(".tar.gz"):
            return f["url"], f["digests"]["sha256"]
    raise RuntimeError(f"No source tarball found for zev {version}")


def get_poet_resources() -> str:
    result = subprocess.run(
        [sys.executable, "-m", "poet", "zev"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"poet failed: {result.stderr}")
    # poet outputs resource blocks including one for zev itself — drop it
    lines = result.stdout.splitlines()
    filtered: list[str] = []
    skip = False
    for line in lines:
        if line.strip().startswith('resource "zev"'):
            skip = True
        if skip:
            if line.strip() == "end":
                skip = False
            continue
        filtered.append(line)
    # strip leading/trailing blank lines
    while filtered and not filtered[0].strip():
        filtered.pop(0)
    while filtered and not filtered[-1].strip():
        filtered.pop()
    return "\n".join(filtered)


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
  depends_on "rust" => :build

{indent(resources)}

  def install
    virtualenv_install_with_resources
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
