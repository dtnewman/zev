import json
import urllib.error
import urllib.request

REQUEST_TIMEOUT_SECONDS = 300


class APIError(Exception):
    """An HTTP error response from an LLM API."""

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


class APIConnectionError(Exception):
    """The LLM API could not be reached."""


def post_json(url: str, body: dict, headers: dict | None = None) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise APIError(e.code, _error_message(e)) from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise APIConnectionError(str(getattr(e, "reason", e))) from e


def _error_message(error: urllib.error.HTTPError) -> str:
    # OpenAI, Azure, Anthropic and Gemini all return {"error": {"message": ...}}
    try:
        data = json.loads(error.read().decode("utf-8"))
        return data["error"]["message"]
    except Exception:
        return error.reason or f"HTTP {error.code}"
