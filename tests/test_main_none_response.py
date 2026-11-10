"""get_options() must tolerate a provider that returns None.

Providers return None when the backend call fails (see
OpenAIProvider.get_options and GeminiProvider.get_options). Saving the
response to history before checking for None crashes with a pydantic
ValidationError instead of returning quietly.
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import zev.main as main_module


class NoneProvider:
    model = "stub-model"

    def get_options(self, prompt, context):
        return None


def test_get_options_none_response_does_not_raise():
    saved = []
    with (
        mock.patch.object(
            main_module, "get_inference_provider", return_value=NoneProvider()
        ),
        mock.patch.object(
            main_module.command_history,
            "save_options",
            side_effect=lambda query, response: saved.append((query, response)),
        ),
    ):
        assert main_module.get_options("do a thing") is None
    assert saved == []
