from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, EmailStr


# --- Auth ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Symptom Logs ---

class LogCreate(BaseModel):
    raw_text: str


class SymptomLogOut(BaseModel):
    id: int
    raw_text: str
    symptoms: List[Any]
    overall_severity: Optional[float]
    logged_at: datetime

    model_config = {"from_attributes": True}


# --- Insights ---

class InsightOut(BaseModel):
    id: int
    insight_type: str
    content: str
    generated_at: datetime

    model_config = {"from_attributes": True}


# --- Dashboard ---

class SymptomFrequency(BaseModel):
    name: str
    count: int


class DashboardOut(BaseModel):
    total_logs: int
    symptom_frequencies: List[SymptomFrequency]
    recent_logs: List[SymptomLogOut]
    latest_insight: Optional[InsightOut]
