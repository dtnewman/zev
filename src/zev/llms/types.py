from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Command:
    command: str
    short_explanation: str
    is_dangerous: bool
    dangerous_explanation: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Command":
        return cls(
            command=data["command"],
            short_explanation=data["short_explanation"],
            is_dangerous=bool(data["is_dangerous"]),
            dangerous_explanation=data.get("dangerous_explanation"),
        )


@dataclass
class OptionsResponse:
    commands: list[Command] = field(default_factory=list)
    is_valid: bool = True
    explanation_if_not_valid: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "OptionsResponse":
        return cls(
            commands=[Command.from_dict(c) for c in data.get("commands") or []],
            is_valid=bool(data["is_valid"]),
            explanation_if_not_valid=data.get("explanation_if_not_valid"),
        )

    def to_dict(self) -> dict:
        return asdict(self)


def _nullable(type_name: str) -> dict:
    return {"anyOf": [{"type": type_name}, {"type": "null"}]}


# Strict JSON schema for OptionsResponse, shared by the OpenAI-compatible and Anthropic providers.
# Strict mode requires every property to be listed in `required` and `additionalProperties: false`;
# optional fields are expressed as nullable instead.
OPTIONS_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "commands": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "short_explanation": {"type": "string"},
                    "is_dangerous": {"type": "boolean"},
                    "dangerous_explanation": _nullable("string"),
                },
                "required": ["command", "short_explanation", "is_dangerous", "dangerous_explanation"],
                "additionalProperties": False,
            },
        },
        "is_valid": {"type": "boolean"},
        "explanation_if_not_valid": _nullable("string"),
    },
    "required": ["commands", "is_valid", "explanation_if_not_valid"],
    "additionalProperties": False,
}
