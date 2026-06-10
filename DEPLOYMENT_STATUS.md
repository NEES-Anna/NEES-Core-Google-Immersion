# Deployment Status

This document clarifies the deployment status of the **NEES Core Engine — Google Immersion Demo**.

## Current Status

* **Public Demo Deployment**: The demo is currently deployed outside Google Cloud for public review.

  * Frontend Demo: https://nees-core-google-immersion.vercel.app
  * Backend API: https://nees-core-google-immersion-api.onrender.com
  * Backend Health Check: https://nees-core-google-immersion-api.onrender.com/health

* **Local Environment**: Fully operational. The frontend and backend can run locally using mock mode when no Gemini API key is provided, allowing easy testing and evaluation without exposing credentials.

* **Google Cloud Run Deployment**: **Planned & Blocked**. The repository includes a Docker-ready backend and a documented Google Cloud Run deployment plan. Live Cloud Run deployment is currently blocked because the current Google Cloud billing account is suspended.

## How to Run Locally

You can run the full application locally in a split-terminal setup.

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the environment variables:

```bash
copy .env.example .env
```

5. Start the server:

```bash
uvicorn app.main:app --reload --port 8000
```

The backend will run at:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Copy the environment variables:

```bash
copy .env.example .env
```

4. Start the development server:

```bash
npm run dev
```

5. Access the web app at:

```text
http://localhost:5173
```

## Cloud Run Deployment Readiness

The backend includes Docker support, and the Google Cloud Run deployment strategy is documented.

Once the billing account issue is resolved, the application can be built and deployed using the steps detailed in:

[docs/cloud-run-deployment-plan.md](docs/cloud-run-deployment-plan.md)

## Notes

This repository does not claim a completed Google Cloud Run deployment during Phase 1. The current public demo is deployed externally for review, while Google Cloud Run deployment is planned as a Phase 2 milestone.
