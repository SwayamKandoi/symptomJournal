import os
from dotenv import load_dotenv
load_dotenv()

from collections import Counter
from datetime import datetime, timedelta, timezone
from functools import wraps

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

import gemini as ai
from auth import create_access_token, get_current_user, hash_password, verify_password
from database import Base, engine, get_db
from models import Insight, SymptomLog, User
from schemas import (
    DashboardOut,
    InsightOut,
    LogCreate,
    SymptomFrequency,
    SymptomLogOut,
    Token,
    UserCreate,
    UserOut,
)

Base.metadata.create_all(bind=engine)

TESTING = os.getenv("TESTING") == "1"
limiter = Limiter(key_func=get_remote_address, default_limits=[] if TESTING else ["200/day", "50/hour"])


def rate_limit(limit_str: str):
    """No-op in test mode, real limit in production."""
    def decorator(func):
        if TESTING:
            return func
        return limiter.limit(limit_str)(func)
    return decorator

app = FastAPI(title="AI Symptom Journal", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_LOG_LENGTH = 1000  # chars


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@rate_limit("5/minute")
def register(request: Request, body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=body.email, hashed_password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token)
@rate_limit("10/minute")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=create_access_token(user.id))


# ---------------------------------------------------------------------------
# Symptom Logging
# ---------------------------------------------------------------------------

@app.post("/logs", response_model=SymptomLogOut, status_code=status.HTTP_201_CREATED)
@rate_limit("20/minute")
def create_log(
    request: Request,
    body: LogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if len(body.raw_text.strip()) == 0:
        raise HTTPException(status_code=422, detail="Log text cannot be empty")
    if len(body.raw_text) > MAX_LOG_LENGTH:
        raise HTTPException(status_code=422, detail=f"Log text exceeds {MAX_LOG_LENGTH} character limit")
    try:
        extracted = ai.extract_symptoms(body.raw_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI error: {exc}")
    log = SymptomLog(
        user_id=current_user.id,
        raw_text=body.raw_text,
        symptoms=extracted.get("symptoms", []),
        overall_severity=extracted.get("overall_severity"),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@app.get("/history", response_model=list[SymptomLogOut])
@rate_limit("60/minute")
def get_history(
    request: Request,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    logs = (
        db.query(SymptomLog)
        .filter(SymptomLog.user_id == current_user.id, SymptomLog.logged_at >= since)
        .order_by(SymptomLog.logged_at.desc())
        .all()
    )
    return logs


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

@app.post("/insights/pattern", response_model=InsightOut)
@rate_limit("5/minute")
def generate_pattern_insight(
    request: Request,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    logs = (
        db.query(SymptomLog)
        .filter(SymptomLog.user_id == current_user.id, SymptomLog.logged_at >= since)
        .order_by(SymptomLog.logged_at.desc())
        .all()
    )
    log_dicts = [
        {"logged_at": str(l.logged_at), "symptoms": l.symptoms, "raw_text": l.raw_text}
        for l in logs
    ]
    try:
        content = ai.generate_pattern_insight(log_dicts, days=days)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI error: {exc}")
    insight = Insight(user_id=current_user.id, insight_type="pattern", content=content)
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


@app.post("/insights/daily", response_model=InsightOut)
@rate_limit("5/minute")
def generate_daily_insight(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    logs_today = (
        db.query(SymptomLog)
        .filter(SymptomLog.user_id == current_user.id, SymptomLog.logged_at >= today_start)
        .all()
    )
    log_dicts = [
        {"logged_at": str(l.logged_at), "symptoms": l.symptoms, "raw_text": l.raw_text}
        for l in logs_today
    ]
    try:
        content = ai.generate_daily_insight(log_dicts)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI error: {exc}")
    insight = Insight(user_id=current_user.id, insight_type="daily", content=content)
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


@app.get("/insights", response_model=list[InsightOut])
@rate_limit("60/minute")
def get_insights(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Insight)
        .filter(Insight.user_id == current_user.id)
        .order_by(Insight.generated_at.desc())
        .limit(20)
        .all()
    )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.get("/dashboard", response_model=DashboardOut)
@rate_limit("60/minute")
def get_dashboard(
    request: Request,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    logs = (
        db.query(SymptomLog)
        .filter(SymptomLog.user_id == current_user.id, SymptomLog.logged_at >= since)
        .order_by(SymptomLog.logged_at.desc())
        .all()
    )

    counter: Counter = Counter()
    for log in logs:
        for symptom in log.symptoms:
            counter[symptom["name"]] += 1

    latest_insight = (
        db.query(Insight)
        .filter(Insight.user_id == current_user.id)
        .order_by(Insight.generated_at.desc())
        .first()
    )

    return DashboardOut(
        total_logs=len(logs),
        symptom_frequencies=[
            SymptomFrequency(name=name, count=count)
            for name, count in counter.most_common(10)
        ],
        recent_logs=logs[:5],
        latest_insight=latest_insight,
    )
