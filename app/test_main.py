"""
Unit tests for AI Symptom Journal backend.
Run with: python -m pytest test_main.py -v
"""
import os
os.environ["TESTING"] = "1"  # must be set before importing main

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

# --------------------------------------------------------------------------
# In-memory SQLite — StaticPool shares one connection so tables persist
# --------------------------------------------------------------------------

TEST_DB_URL = "sqlite://"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

MOCK_EXTRACTED = {
    "symptoms": [
        {"name": "headache", "severity": 7, "location": "frontal", "duration": "2h"},
        {"name": "fatigue", "severity": 5, "location": None, "duration": None},
    ],
    "overall_severity": 6.0,
}


def register_and_login(email="test@example.com", password="testpass123"):
    client.post("/auth/register", json={"email": email, "password": password})
    resp = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ==========================================================================
# Auth
# ==========================================================================

class TestRegister:
    def test_register_success(self):
        resp = client.post("/auth/register", json={"email": "a@b.com", "password": "pass1234"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "a@b.com"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self):
        client.post("/auth/register", json={"email": "dup@b.com", "password": "pass1234"})
        resp = client.post("/auth/register", json={"email": "dup@b.com", "password": "pass1234"})
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"]

    def test_register_invalid_email(self):
        resp = client.post("/auth/register", json={"email": "not-an-email", "password": "pass1234"})
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self):
        client.post("/auth/register", json={"email": "login@test.com", "password": "mypassword"})
        resp = client.post(
            "/auth/login",
            data={"username": "login@test.com", "password": "mypassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert resp.json()["token_type"] == "bearer"

    def test_login_wrong_password(self):
        client.post("/auth/register", json={"email": "login2@test.com", "password": "correct"})
        resp = client.post(
            "/auth/login",
            data={"username": "login2@test.com", "password": "wrong"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 401

    def test_login_unknown_user(self):
        resp = client.post(
            "/auth/login",
            data={"username": "nobody@test.com", "password": "pass"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 401

    def test_protected_route_without_token(self):
        resp = client.get("/dashboard")
        assert resp.status_code == 401

    def test_protected_route_bad_token(self):
        resp = client.get("/dashboard", headers={"Authorization": "Bearer fake.token.here"})
        assert resp.status_code == 401


# ==========================================================================
# Symptom Logging
# ==========================================================================

class TestLog:
    def test_log_success(self):
        token = register_and_login()
        with patch("gemini.extract_symptoms", return_value=MOCK_EXTRACTED):
            resp = client.post(
                "/logs",
                json={"raw_text": "I have a headache and feel tired"},
                headers=auth_headers(token),
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["raw_text"] == "I have a headache and feel tired"
        assert len(data["symptoms"]) == 2
        assert data["symptoms"][0]["name"] == "headache"
        assert data["overall_severity"] == 6.0

    def test_log_empty_text(self):
        token = register_and_login()
        resp = client.post(
            "/logs",
            json={"raw_text": "   "},
            headers=auth_headers(token),
        )
        assert resp.status_code == 422

    def test_log_text_too_long(self):
        token = register_and_login()
        resp = client.post(
            "/logs",
            json={"raw_text": "x" * 1001},
            headers=auth_headers(token),
        )
        assert resp.status_code == 422

    def test_log_ai_error_returns_500(self):
        token = register_and_login()
        with patch("gemini.extract_symptoms", side_effect=Exception("API down")):
            resp = client.post(
                "/logs",
                json={"raw_text": "My back hurts"},
                headers=auth_headers(token),
            )
        assert resp.status_code == 500
        assert "AI error" in resp.json()["detail"]

    def test_log_requires_auth(self):
        resp = client.post("/logs", json={"raw_text": "headache"})
        assert resp.status_code == 401


class TestHistory:
    def test_history_empty(self):
        token = register_and_login()
        resp = client.get("/history", headers=auth_headers(token))
        assert resp.status_code == 200
        assert resp.json() == []

    def test_history_returns_own_logs_only(self):
        token1 = register_and_login("user1@test.com", "pass1")
        token2 = register_and_login("user2@test.com", "pass2")

        with patch("gemini.extract_symptoms", return_value=MOCK_EXTRACTED):
            client.post("/logs", json={"raw_text": "user1 headache"}, headers=auth_headers(token1))
            client.post("/logs", json={"raw_text": "user2 backpain"}, headers=auth_headers(token2))

        resp1 = client.get("/history", headers=auth_headers(token1))
        assert len(resp1.json()) == 1
        assert resp1.json()[0]["raw_text"] == "user1 headache"

        resp2 = client.get("/history", headers=auth_headers(token2))
        assert len(resp2.json()) == 1
        assert resp2.json()[0]["raw_text"] == "user2 backpain"


# ==========================================================================
# Insights
# ==========================================================================

class TestInsights:
    def test_daily_insight(self):
        token = register_and_login()
        with patch("gemini.extract_symptoms", return_value=MOCK_EXTRACTED):
            client.post("/logs", json={"raw_text": "tired and sore"}, headers=auth_headers(token))

        with patch("gemini.generate_daily_insight", return_value="You had a tough day. Rest well."):
            resp = client.post("/insights/daily", headers=auth_headers(token))

        assert resp.status_code == 200
        data = resp.json()
        assert data["insight_type"] == "daily"
        assert data["content"] == "You had a tough day. Rest well."

    def test_pattern_insight(self):
        token = register_and_login()
        with patch("gemini.extract_symptoms", return_value=MOCK_EXTRACTED):
            client.post("/logs", json={"raw_text": "headache again"}, headers=auth_headers(token))

        with patch("gemini.generate_pattern_insight", return_value="Headaches appear frequently."):
            resp = client.post("/insights/pattern", headers=auth_headers(token))

        assert resp.status_code == 200
        assert resp.json()["insight_type"] == "pattern"

    def test_get_insights_list(self):
        token = register_and_login()
        with patch("gemini.generate_daily_insight", return_value="Feeling okay today."):
            client.post("/insights/daily", headers=auth_headers(token))
        with patch("gemini.generate_daily_insight", return_value="Better than yesterday."):
            client.post("/insights/daily", headers=auth_headers(token))

        resp = client.get("/insights", headers=auth_headers(token))
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_insight_ai_error(self):
        token = register_and_login()
        with patch("gemini.generate_daily_insight", side_effect=Exception("timeout")):
            resp = client.post("/insights/daily", headers=auth_headers(token))
        assert resp.status_code == 500
        assert "AI error" in resp.json()["detail"]


# ==========================================================================
# Dashboard
# ==========================================================================

class TestDashboard:
    def test_dashboard_empty(self):
        token = register_and_login()
        resp = client.get("/dashboard", headers=auth_headers(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_logs"] == 0
        assert data["symptom_frequencies"] == []
        assert data["recent_logs"] == []
        assert data["latest_insight"] is None

    def test_dashboard_counts_symptoms(self):
        token = register_and_login()
        with patch("gemini.extract_symptoms", return_value=MOCK_EXTRACTED):
            client.post("/logs", json={"raw_text": "headache and tired"}, headers=auth_headers(token))
            client.post("/logs", json={"raw_text": "headache again"}, headers=auth_headers(token))

        resp = client.get("/dashboard", headers=auth_headers(token))
        data = resp.json()
        assert data["total_logs"] == 2
        freqs = {f["name"]: f["count"] for f in data["symptom_frequencies"]}
        assert freqs["headache"] == 2
        assert freqs["fatigue"] == 2

    def test_dashboard_shows_latest_insight(self):
        token = register_and_login()
        with patch("gemini.generate_daily_insight", return_value="Take it easy today."):
            client.post("/insights/daily", headers=auth_headers(token))

        resp = client.get("/dashboard", headers=auth_headers(token))
        assert resp.json()["latest_insight"]["content"] == "Take it easy today."

    def test_dashboard_recent_logs_capped_at_5(self):
        token = register_and_login()
        with patch("gemini.extract_symptoms", return_value=MOCK_EXTRACTED):
            for i in range(7):
                client.post("/logs", json={"raw_text": f"log {i}"}, headers=auth_headers(token))

        resp = client.get("/dashboard", headers=auth_headers(token))
        assert len(resp.json()["recent_logs"]) == 5
