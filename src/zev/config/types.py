from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple


@dataclass
class SetupQuestionSelectOption:
    """Represents a possible answer to a question"""

    value: str
    label: str
    description: Optional[str] = None
    follow_up_questions: Tuple["SetupQuestion", ...] = ()


@dataclass
class SetupQuestion:
    name: str
    prompt: str


@dataclass
class SetupQuestionSelect(SetupQuestion):
    """Prompts the user with a select menu"""

    options: List[SetupQuestionSelectOption]


@dataclass
class SetupQuestionText(SetupQuestion):
    """Prompts the user to enter text"""

    validator: Optional[Callable] = None  # a function that takes answer and returns a bool
    default: Optional[str] = ""
