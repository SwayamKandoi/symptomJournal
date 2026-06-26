import json
import os
from typing import Any, Dict, List

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = "gpt-4o-mini"
MAX_INPUT_CHARS = 1000  # hard cap on user text sent to OpenAI


def _chat(system: str, user: str, max_tokens: int = 512) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user[:MAX_INPUT_CHARS]},
        ],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


EXTRACT_SYSTEM = """\
You are a medical symptom extractor. Given a user's free-text health note, return ONLY a valid JSON object with this exact shape:
{
  "symptoms": [
    {
      "name": "<symptom name, lowercase>",
      "severity": <integer 1-10 or null if not mentioned>,
      "location": "<body location or null>",
      "duration": "<duration string or null>"
    }
  ],
  "overall_severity": <float average of non-null severities, or null>
}
Rules: extract every distinct symptom mentioned; do not add symptoms not mentioned; severity 1=barely noticeable, 10=severe; return ONLY the JSON, no markdown fences, no explanation."""

PATTERN_SYSTEM = "You are a health pattern analyst. Be concise, friendly, and non-alarmist. Do NOT diagnose."

DAILY_SYSTEM = "You are a supportive health coach. Be warm and concise. Do NOT diagnose."


def extract_symptoms(text: str) -> Dict[str, Any]:
    raw = _chat(EXTRACT_SYSTEM, text, max_tokens=512)
    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate_pattern_insight(logs: List[Dict[str, Any]], days: int = 30) -> str:
    log_lines = [
        f"- {l['logged_at'][:10]}: {', '.join(s['name'] for s in l.get('symptoms', [])) or 'no structured symptoms'}"
        for l in logs
    ]
    summary = "\n".join(log_lines[:50]) or "No logs yet."  # cap at 50 entries
    user_msg = (
        f"The user has logged symptoms over the past {days} days (most recent first):\n{summary}\n\n"
        "Write a concise plain-English paragraph (3-5 sentences) that: "
        "1) Names any symptoms appearing more than twice. "
        "2) Notes any worsening or improving trends. "
        "3) Suggests one actionable step."
    )
    return _chat(PATTERN_SYSTEM, user_msg, max_tokens=300)


def generate_daily_insight(logs_today: List[Dict[str, Any]]) -> str:
    log_lines = [
        f"- {', '.join(s['name'] for s in l.get('symptoms', [])) or 'general note'}: {l['raw_text'][:80]}"
        for l in logs_today
    ]
    summary = "\n".join(log_lines) or "No logs today."
    user_msg = (
        f"Today's symptom log:\n{summary}\n\n"
        "Write a single encouraging paragraph (2-3 sentences) summarising how the user felt today "
        "and one small self-care tip relevant to their symptoms."
    )
    return _chat(DAILY_SYSTEM, user_msg, max_tokens=200)
