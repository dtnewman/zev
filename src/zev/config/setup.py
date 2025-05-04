from pathlib import Path
from typing import Dict

import questionary
from dotenv import dotenv_values

from zev.config.types import (
    SetupQuestion,
    SetupQuestionSelect,
    SetupQuestionSelectOption,
    SetupQuestionText,
)
from zev.constants import LLMProviders
from zev.llms.azure_openai.setup import questions as azure_questions
from zev.llms.gemini.setup import questions as gemini_questions
from zev.llms.ollama.setup import questions as ollama_questions
from zev.llms.openai.setup import questions as openai_questions

setup_questions = [
    SetupQuestionSelect(
        name="LLM_PROVIDER",
        prompt="Pick your LLM provider:",
        options=[
            SetupQuestionSelectOption(
                value=LLMProviders.OPENAI,
                label="OpenAI",
                follow_up_questions=openai_questions,
            ),
            SetupQuestionSelectOption(
                value=LLMProviders.OLLAMA,
                label="Ollama",
                follow_up_questions=ollama_questions,
            ),
            SetupQuestionSelectOption(
                value=LLMProviders.GEMINI,
                label="Gemini",
                follow_up_questions=gemini_questions,
            ),
            SetupQuestionSelectOption(
                value=LLMProviders.AZURE_OPENAI,
                label="Azure OpenAI",
                follow_up_questions=azure_questions,
            ),
        ],
    )
]


def prompt_question(question: SetupQuestion, answers: Dict[str, str]) -> Dict[str, str]:
    existing_answer = answers.get(question.name)
    if isinstance(question, SetupQuestionSelect):
        selected_option: SetupQuestionSelectOption = questionary.select(
            question.prompt,
            choices=[
                questionary.Choice(option.label, description=option.description, value=option)
                for option in question.options
            ],
        ).ask()

        answers[question.name] = selected_option.value
        for q in selected_option.follow_up_questions:
            answers.update(prompt_question(q, answers=answers))
    elif isinstance(question, SetupQuestionText):
        answer = questionary.text(
            question.prompt,
            default=existing_answer or question.default or "",
            validate=question.validator,
        ).ask()
        answers[question.name] = answer
    else:
        raise Exception("Invalid question type")
    return answers


def run_setup():
    config_path = Path.home() / ".zevrc"
    answers = dotenv_values(config_path)  # load in current values and then override as necessary
    for question in setup_questions:
        answers.update(prompt_question(question, answers))

    new_file = ""
    for env_var_name, value in answers.items():
        new_file += f"{env_var_name}={value}\n"

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(new_file)
