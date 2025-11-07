from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

# ==== Données persistées en Pickle ==========================================

@dataclass
class User:
    email: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Question:
    num: int
    owner_email: str
    title: str
    statement: str
    attachments: list[str] = field(default_factory=list)
    expected_answer: str = ""
    required_points: list[Any] = field(default_factory=list)     # str ou {"type":"regex","value":"..."}
    forbidden_points: list[Any] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PublicLink:
    code: str
    question_num: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

@dataclass
class Attempt:
    question_num: int
    student_email: str
    answer_text: str
    auto_score: float
    auto_feedback: str
    created_at: datetime = field(default_factory=datetime.utcnow)


# ==== Adaptateur pour Flask-Login ============================================

class LoginUser:
    """
    Petit wrapper autour de User pour satisfaire Flask-Login
    (get_id/is_authenticated/...).
    """
    def __init__(self, user: User):
        self._user = user
        self.email = user.email

    # Flask-Login interface
    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> str:
        return self._user.email
