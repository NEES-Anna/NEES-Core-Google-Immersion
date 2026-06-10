# Backend

FastAPI service for the NEES Core Engine — Google Immersion Demo.

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

## Test

```bash
pytest
```

The service works without `GEMINI_API_KEY` when `MOCK_GEMMA_WHEN_MISSING_KEY=true`.
