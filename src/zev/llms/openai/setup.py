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
                value="gpt-6-luna",
                label="gpt-6-luna",
                description="Fastest and cheapest, great for most tasks",
            ),
            SetupQuestionSelectOption(
                value="gpt-6.1-terra",
                label="gpt-6.1-terra",
                description="Fast and efficient, a step up in capability",
            ),
            SetupQuestionSelectOption(
                value="gpt-6.2-astra",
                label="gpt-6.2-astra",
                description="Flagship model for complex reasoning and coding",
            ),
        ],
    ),
)
