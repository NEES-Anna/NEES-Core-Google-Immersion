# Deployment Status — Google Cloud Run

This document clarifies the deployment status of the NEES Core Engine — Google Immersion Demo.

## Current Status

* **Local Environment**: Fully operational. The frontend and backend run locally using a mock fallback mode when no Gemini API key is provided, allowing for easy testing and evaluation.
* **Google Cloud Run Deployment**: **Planned & Blocked**. The deployment to Google Cloud Run is fully designed, and Docker configurations are ready. However, live deployment is currently blocked because the Google Cloud billing account is suspended.

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

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Access the web app at `http://localhost:5173`.

## Cloud Run Deployment Readiness

The dockerization and cloud deployment strategy are fully planned. As soon as the billing account issue is resolved, the application can be built and deployed using the steps detailed in [docs/cloud-run-deployment-plan.md](file:///d:/Nainacore/apps/NEES-Core-Google-Immersion/docs/cloud-run-deployment-plan.md).
