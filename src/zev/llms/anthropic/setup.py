from zev.config.types import (
    SetupQuestionSelect,
    SetupQuestionSelectOption,
    SetupQuestionText,
)

questions = (
    SetupQuestionText(
        name="ANTHROPIC_API_KEY",
        prompt="Your ANTHROPIC api key:",
        default="",
    ),
    SetupQuestionSelect(
        name="ANTHROPIC_MODEL",
        prompt="Choose which model you would like to default to:",
        options=[
            SetupQuestionSelectOption(
                value="claude-opus-5-5",
                label="claude-opus-5-5",
                description="Most capable Opus model, best quality",
            ),
            SetupQuestionSelectOption(
                value="claude-sonnet-5-5",
                label="claude-sonnet-5-5",
                description="Balance of speed and capability",
            ),
            SetupQuestionSelectOption(
                value="claude-haiku-5-5",
                label="claude-haiku-5-5",
                description="Fastest and cheapest option",
            ),
        ],
    ),
)
