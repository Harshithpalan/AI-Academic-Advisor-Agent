# AI Academic Advisor Agent

A web app that acts as an academic advisor for a BS Computer Science student.

## Features

- **Chat advisor** — ask "What should I take next?", "What's my GPA?", "Tell me about CS410", "I'm interested in machine learning", "Build me a plan"
- **Profile** — record completed courses + grades, max credits/semester, next term
- **Degree Audit** — per-requirement progress (core, math, science sequence, electives, breadth) with % toward 120 credits
- **Plan** — greedy semester-by-semester schedule honoring prerequisites, term offerings, and the credit cap

## Run

```bash
pip install -r requirements.txt
uvicorn app:app --port 8000
# open http://localhost:8000
```

## Layout

- `catalog.py` — course catalog (prereqs, terms, categories) + degree requirements
- `advisor.py` — engine: GPA, audit, recommendations, planner, chat intents
- `app.py` — FastAPI endpoints + static file serving
- `static/index.html` — single-page UI (no build step)

## Notes

Sessions are in-memory and keyed by a token in `localStorage`; restart wipes them.
The advisor is rule-based (deterministic). To wire in an LLM for free-form chat,
add an API key and extend `advisor.respond` as a fallback before the canned reply.
