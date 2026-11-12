from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class QuestionCategory(str, Enum):
    INTRODUCTION = "Introduction"
    EDUCATION = "Education"
    EXPERIENCE = "Experience"
    SKILLS = "Skills"
    LOCATION = "Location"
    SALARY = "Salary"
    NOTICE_PERIOD = "Notice period"


class AnswerType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    CHOICE = "choice"
    DURATION = "duration"
    CURRENCY_RANGE = "currency_range"
    RATING = "rating"


class ImportanceLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ValidationRules(BaseModel):
    min_word_count: Optional[int] = None
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    min_expected_value: Optional[float] = None
    max_expected_value: Optional[float] = None
    valid_choices: Optional[List[str]] = None
    required_keywords: Optional[List[str]] = None
    extract_entities: Optional[List[str]] = None


class ScreeningQuestion(BaseModel):
    id: str
    category: QuestionCategory
    role: str = "General"
    intent: str
    template: str
    expected_answer_type: AnswerType
    is_mandatory: bool = True
    scoring_importance: ImportanceLevel = ImportanceLevel.HIGH
    weight: float = 1.0
    validation_rules: Optional[ValidationRules] = None
    multilingual: Dict[str, str] = Field(default_factory=dict)
    follow_up_prompt: Optional[str] = None

    def render(self, context: Dict[str, Any], lang: str = "en") -> str:
        """Render question with candidate/job context in requested language."""
        raw_text = self.multilingual.get(lang) or self.template
        for key, val in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in raw_text:
                raw_text = raw_text.replace(placeholder, str(val))
        return raw_text


class ScreeningCallScriptItem(BaseModel):
    stage_id: str
    category: str
    question_id: Optional[str] = None
    rendered_prompt: str
    expected_answer_type: str
    is_mandatory: bool
    scoring_importance: str
    intent: Optional[str] = None
    follow_up_prompt: Optional[str] = None


class ScreeningCallScript(BaseModel):
    candidate_name: str
    role_name: str
    language: str
    total_stages: int
    estimated_call_duration_minutes: float
    script_items: List[ScreeningCallScriptItem]
    closing_statement: str
