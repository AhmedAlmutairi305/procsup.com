# China University Application Agent (Semi-Automatic, Local)

Production-style local MVP for preparing, tracking, and semi-automating Chinese university applications with **explicit human approval gates** before irreversible submission.

## Architecture Summary

### Core stack
- **Backend API:** FastAPI
- **Automation:** Playwright
- **Database:** SQLite + SQLAlchemy
- **Validation/Contracts:** Pydantic
- **Dashboard:** Server-rendered Jinja2 + minimal CSS
- **Config:** `.env` via `pydantic-settings`
- **Logging/Audit:** Rotating app log + database audit events

### Safety model
1. Automation defaults to **dry-run**.
2. Agent fills and uploads in preview/preparation mode.
3. Agent always pauses at **human review gate** before final submit.
4. Final submission can only be marked complete through explicit manual approval endpoint/UI action.
5. CAPTCHA detection pauses and requests manual intervention.

### Key modules
- `app/services/requirement_parser.py`: Requirement extraction from raw text.
- `app/services/document_matcher.py`: File-tag and name based robust matching with confidence + mismatch warnings.
- `app/automation/playwright_agent.py`: Browser workflow with retries, selector fallbacks, screenshots, pause gates.
- `app/api/routes.py`: CRUD + parsing + automation + tracking endpoints.
- `app/templates/*`: Dashboard and university profile UI.

## Project Tree

```text
.
├── app
│   ├── api/routes.py
│   ├── automation/playwright_agent.py
│   ├── core/{config.py,logging.py}
│   ├── db/{database.py,init_db.py}
│   ├── models/models.py
│   ├── schemas/schemas.py
│   ├── services/{audit.py,credentials.py,csv_importer.py,document_matcher.py,email_drafts.py,requirement_parser.py}
│   ├── static/dashboard.css
│   ├── templates/{base.html,dashboard.html,university.html}
│   └── main.py
├── data/{logs,screenshots,seed,uploads}
├── examples
│   ├── universities_sample.csv
│   └── document_library/{README.md,*.pdf}
├── scripts/seed_data.py
├── .env.example
├── requirements.txt
└── README.md
```

## Features Implemented

### 1) University Management
- Add universities via API.
- Import from CSV.
- Track portal URL, deadline, degree level, language, scholarship, fee, recommendation count, status.

### 2) Requirement Parsing
- Accept raw text from portal/announcement pages.
- Extract and structure:
  - required documents,
  - deadline,
  - language requirement,
  - application fee,
  - recommendation letter count,
  - boolean flags for study plan/CV/passport/transcript/medical form.

### 3) Document Manager
- Upload files into central library.
- Tag each file by document type.
- Match required documents to files with confidence score.
- Surface missing items and naming mismatch warnings.
- Preview upload mapping.

### 4) Browser Automation (Playwright)
- Opens portal and navigates with retry logic.
- Selector fallback strategy for filling and uploads.
- Captures screenshots at key steps.
- Logs selector failures/page-change issues.
- Detects CAPTCHA and pauses.
- Pauses before final submission and requires explicit approval event.

### 5) Dashboard
- University and application overview.
- University detail with requirement parser form.
- Trigger automation by university ID.
- Approve/reject final submission manually.
- Inspect audit logs and screenshots.

### 6) Tracking & Audit Trail
- Every major action persisted in `audit_logs` with timestamp.
- Store statuses, pending items, submitted vs prepared-only state.
- Follow-up email draft generation endpoint.

### 7) AI Hook Ready
- LLM-specific logic isolated behind service boundaries (`services/*`).
- Current system works fully without LLMs.

## Setup

1. **Create environment and install dependencies**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Install Playwright browsers**
```bash
playwright install chromium
```

3. **Configure environment**
```bash
cp .env.example .env
# then edit .env as needed
```

4. **Initialize and seed local data**
```bash
python scripts/seed_data.py
```

5. **Run app**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

6. **Open dashboard and docs**
- Dashboard: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`

## Usage Workflow

1. Import universities from CSV (`examples/universities_sample.csv`) or add manually via API.
2. Upload documents to library (`/api/documents/upload`).
3. Paste requirement text in university profile page; parser stores structured requirement.
4. Start automation from dashboard (dry-run recommended first).
5. Review logs/screenshots and document match preview.
6. If ready, manually approve final submit in dashboard/API.
7. Track post-submission status and generate follow-up emails.

## API Highlights

- `GET /api/universities`
- `POST /api/universities`
- `POST /api/universities/import-csv`
- `POST /api/requirements/parse`
- `POST /api/documents/upload`
- `GET /api/universities/{id}/match-preview`
- `POST /api/automation/start`
- `POST /api/automation/final-submit`
- `GET /api/applications/{id}/logs`
- `GET /api/applications/{id}/follow-up-email`

## Secure Credential Pattern

- No plaintext passwords in code or DB.
- `CredentialProvider` reads credentials from environment variables per university slug.
- Can be replaced later with OS keyring or vault integration.

## Future Improvements

- Richer form recipe engine per university with maintained selector maps.
- Native keyring integration for credentials.
- OCR support for scanned documents.
- Real multilingual translation/summarization via pluggable LLM provider.
- Background job queue (Celery/RQ) for long automation runs.
- WebSocket live run monitor.
- Role-based local auth for multi-user operation.

## Known Limitations

- Generic automation uses fallback selectors and may require per-portal tuning.
- CAPTCHA solving is manual by design.
- Final real submit click is represented as explicit approval event to enforce safety.
- SQLite is default for local single-user MVP; migrate to PostgreSQL for multi-user concurrency.
