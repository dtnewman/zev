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
                value="gpt-5.4-mini",
                label="gpt-5.4-mini",
                description="Fast and cost-efficient, great for most tasks",
            ),
            SetupQuestionSelectOption(
                value="gpt-5.4",
                label="gpt-5.4",
                description="Flagship model for complex reasoning and coding",
            ),
            SetupQuestionSelectOption(
                value="gpt-5.4-nano",
                label="gpt-5.4-nano",
                description="Cheapest option, best for simple high-volume tasks",
            ),
        ],
    ),
)
