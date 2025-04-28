from zev.config.types import SetupQuestionText, SetupQuestionSelect, SetupQuestionSelectOption
 
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
            value="gemini-1.5-flash", label="gemini-1.5-flash", description="Low Latency, Good for summarization, Good Performance"
            ),
            SetupQuestionSelectOption(
            value="gemini-2.0-flash", label="gemini-2.0-flash", description="Long Context, Good Performance"
            ),
        ],
    ),
 )