from zev.config.types import (
    SetupQuestionSelect,
    SetupQuestionSelectOption,
    SetupQuestionText,
)

questions = (
    SetupQuestionText(
        name="GEMINI_API_KEY",
        prompt="Your GEMINI api key:",
        default="",
    ),
    SetupQuestionSelect(
        name="GEMINI_MODEL",
        prompt="Choose which model you would like to default to:",
        options=[
            SetupQuestionSelectOption(
                value="gemini-3-flash-preview",
                label="gemini-3-flash-preview",
                description="Frontier-class performance at a fraction of the cost",
            ),
            SetupQuestionSelectOption(
                value="gemini-3.1-flash-lite-preview",
                label="gemini-3.1-flash-lite-preview",
                description="Fastest and most budget-friendly option",
            ),
        ],
    ),
)
