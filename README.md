# SymptomJournal

> Talk to your journal. Let AI listen.

SymptomJournal is an AI-powered symptom tracking app. Instead of filling out forms and dropdowns, you describe how you feel in plain English — AI extracts structured symptom data, tracks patterns over time, and generates plain-language insights you can bring to a doctor.

Built for a hackathon in under 24 hours.

## Features

- **Natural language logging** — type how you feel, AI (GPT-4o-mini) extracts symptom name, severity (1-10), location, and duration
- **Dashboard** — bar chart of symptom frequency, stats on total logs and top symptoms
- **Daily insights** — AI-generated plain-English summary of how you felt that day
- **Pattern detection** — 30-day analysis that flags recurring symptoms and suggests when to see a doctor
- **Secure auth** — JWT-based register/login with bcrypt password hashing
- **Rate limiting** — protects the OpenAI budget from abuse

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, SQLite, Pydantic, Uvicorn |
| AI | OpenAI API (GPT-4o-mini) |
| Auth | JWT (python-jose), bcrypt |
| Rate limiting | SlowAPI |
| Frontend | React, Vite, Tailwind CSS, React Router, Recharts |
| Testing | pytest (23 unit tests, mocked AI calls) |

## Project Structure

```
brain/
├── app/                  # FastAPI backend
│   ├── main.py           # App entrypoint, routes, rate limiting
│   ├── models.py         # SQLAlchemy models (User, SymptomLog, Insight)
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── auth.py           # JWT + bcrypt auth logic
│   ├── gemini.py         # OpenAI integration (symptom extraction, insights)
│   ├── database.py       # SQLite engine/session
│   ├── test_main.py      # Unit tests
│   └── requirements.txt
└── frontend/             # React + Vite frontend
    └── src/
        ├── pages/         # Landing, Login, Register, Dashboard, LogSymptom, Insights
        ├── components/    # Navbar, LogCard, SymptomChart
        └── api.js         # Axios client
```

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- An OpenAI API key

### Backend

```bash
cd app
python -m pip install -r requirements.txt
```

Create `app/.env`:

```
OPENAI_API_KEY=your_openai_key_here
SECRET_KEY=your_random_secret_key_here
```

Run the server:

```bash
python -m uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and proxies API requests to the backend.

### Running Tests

```bash
cd app
python -m pytest test_main.py -v
```

23 tests covering auth, logging, history, insights, and dashboard — all AI calls are mocked, so no API key or quota is consumed.

## How It Works

1. User logs a symptom in plain text (e.g. *"splitting headache since noon, maybe a 7/10, and really tired"*)
2. The text is sent to GPT-4o-mini with a structured prompt that returns symptom name, severity, location, and duration as JSON
3. The structured log is stored and visualized on the dashboard
4. On demand, the user can generate a **daily insight** (summary of today) or a **pattern insight** (30-day trend analysis with recommendations)

## What's Next

- Trend lines per symptom over time
- One-page PDF export formatted for doctor visits
- Wearable integration (Apple Health / Fitbit)
- Medication tracking with AI-correlated relief analysis
- Native mobile app

## License

Built for hackathon purposes.
