# Foreign Job Hunter AI — Combined Production Build

Includes:
1. Cloud-database-ready persistence (DATABASE_URL configuration; SQLite fallback for local development).
2. Password authentication with hashed passwords and expiring-style signed session payloads for the starter.
3. Scheduled-sync endpoint protected by CRON_SECRET; configure your hosting scheduler to call source adapters.
4. DOCX + PDF tailored CV generation and tailored cover-letter generation.
5. Application queue and status tracker.
6. Greenhouse and Lever job-source adapters.
7. Docker + Render deployment configuration.
8. Human approval gate before application submission.

## Local
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
Open http://127.0.0.1:8000

## Cloud
Set DATABASE_URL to a managed PostgreSQL connection in production.
Set CRON_SECRET and OPENAI_API_KEY as secrets.
Configure scheduled calls to the permitted source endpoints.

## Public HTTPS
The package is deployment-ready but cannot create a public URL without a hosting account being connected/authorized. Deploy the repo to your hosting provider using the included Dockerfile/render.yaml.

## Application automation
The assistant may prepare fields and documents, but final submission remains human-controlled. Never bypass CAPTCHAs, anti-bot systems, access restrictions, or employer legal attestations.
