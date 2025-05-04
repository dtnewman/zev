from zev.config.types import (
    SetupQuestionSelect,
    SetupQuestionSelectOption,
    SetupQuestionText,
)

questions = (
    SetupQuestionText(
        name="OPENAI_API_KEY",
        prompt="Your OPENAI api key:",
        default="",
    ),
    SetupQuestionSelect(
        name="OPENAI_MODEL",
        prompt="Choose which model you would like to default to:",
        options=[
            SetupQuestionSelectOption(
                value="gpt-4o-mini",
                label="gpt-4o-mini",
                description="Good performance and speed, and cheaper",
            ),
            SetupQuestionSelectOption(
                value="gpt-4o",
                label="gpt-4o",
                description="More expensive and slower, but better performance",
            ),
        ],
    ),
)
