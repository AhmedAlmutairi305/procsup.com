# China University Application Agent (Upgraded Local MVP)

A Windows-friendly, browser-first **FastAPI + Playwright + SQLite** local agent that helps users semi-automate Chinese university applications with mandatory human approval at critical steps.

## Architecture Summary

- **Backend:** FastAPI (REST + WebSocket stream for live runs)
- **Automation:** Playwright (headed by default) + Windows desktop fallback abstraction (`pywinauto`)
- **DB:** SQLite + SQLAlchemy models for applicants, runs/sessions, events, screenshots, manual approvals, audit
- **Dashboard:** Jinja templates (`/`, `/runs/{id}`) for live run monitor and controls
- **Applicant input:** Excel/CSV import via `pandas` + `openpyxl`
- **Mapping layer:** canonical applicant profile → recipe-driven portal selectors with normalization/transforms
- **Documents:** deterministic routing (explicit path priority, tag fallback, pre-run warnings)
- **Email verification:** IMAP polling service with code/link extraction + manual override gates
- **Credential security:** keyring-first secret provider with env fallback; no hardcoded plaintext passwords

## Upgrade Summary

Implemented major upgrades while preserving existing endpoints and behavior:

1. Added applicant profile model/import pipeline for `.xlsx` and `.csv`.
2. Added automation session/run model with statuses:
   - queued, preparing, running, waiting_manual_action, waiting_email_verification, paused, completed, failed, cancelled.
3. Added real-time run events + screenshots + WebSocket stream (`/api/ws/runs/{run_id}`).
4. Added live monitor page with pause/resume/cancel and manual action approvals.
5. Added mapping layer + normalization utilities + recipe override support.
6. Added document routing plan with local path validation and fallback tag matching.
7. Upgraded Playwright agent to session-driven workflow with explicit manual gates.
8. Added Windows desktop fallback abstraction using `pywinauto` for native file picker scenarios.
9. Added IMAP email verification polling service.
10. Added recipe management endpoints and sample recipes (2 university examples + generic fallback).
11. Added baseline pytest suite (normalization/parser/mapper/document routing/session API smoke).

## File Tree

```text
.
├── app/
│   ├── api/routes.py
│   ├── automation/
│   │   ├── desktop_fallback.py
│   │   └── playwright_agent.py
│   ├── core/config.py
│   ├── db/{database.py,init_db.py}
│   ├── models/models.py
│   ├── schemas/schemas.py
│   ├── services/
│   │   ├── audit.py
│   │   ├── credentials.py
│   │   ├── document_router.py
│   │   ├── email_verification.py
│   │   ├── excel_importer.py
│   │   ├── field_mapper.py
│   │   ├── normalization.py
│   │   ├── recipe_loader.py
│   │   ├── run_hub.py
│   │   └── secrets.py
│   ├── templates/{dashboard.html,run_live.html,university.html,base.html}
│   └── main.py
├── examples/
│   ├── applicant_template.csv
│   └── recipes/{generic.json,tsinghua-university.json,zhejiang-university.json}
├── tests/
│   ├── test_api_smoke.py
│   ├── test_document_router.py
│   ├── test_excel_importer.py
│   ├── test_field_mapper.py
│   └── test_normalization.py
├── requirements.txt
├── .env.example
└── README.md
```

## Windows Setup (PowerShell and CMD)

### 1) Create virtual environment

PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

CMD:
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Install Playwright browser

```powershell
playwright install chromium
```

### 4) Configure env

PowerShell:
```powershell
Copy-Item .env.example .env
```

CMD:
```cmd
copy .env.example .env
```

### 5) (Optional) Seed universities

```powershell
python scripts/seed_data.py
```

### 6) Run server

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Run Steps (End-to-End)

1. Open dashboard: `http://127.0.0.1:8000/`.
2. Import applicant Excel/CSV (absolute Windows path, e.g. `C:\\Users\\...\\applicants.xlsx`).
3. Ensure university has a slug that maps to recipe files (or generic fallback recipe is used).
4. Start run with university + applicant + dry_run/headed.
5. Monitor live updates on `/runs/{run_id}`.
6. Resolve manual actions (login submit, email verification continue, final submit) on the run page.
7. Pause/resume/cancel as needed.
8. Inspect logs/events/screenshots through API endpoints.

## API Highlights (Expanded)

- Applicant profiles:
  - `POST /api/applicants/import`
  - `POST /api/applicants/parse`
  - `GET /api/applicants`
  - `GET /api/applicants/{id}`
  - `PUT /api/applicants/{id}`
- Mapping/document preview:
  - `GET /api/mapping/preview?university_id=...&applicant_profile_id=...`
- Run sessions:
  - `POST /api/automation/start`
  - `GET /api/runs`
  - `GET /api/runs/{id}`
  - `GET /api/runs/{id}/events`
  - `GET /api/runs/{id}/screenshots`
  - `POST /api/runs/{id}/pause|resume|cancel`
  - `POST /api/manual-actions/resolve`
  - `WS /api/ws/runs/{run_id}`
- Email verification:
  - `GET /api/email-verification/poll`
- Recipes:
  - `GET /api/recipes`
  - `GET /api/recipes/{slug}`
  - `POST /api/recipes/{slug}`

## Credentials / Security

- Recommended: store portal/email secrets in OS keyring.
- Fallback env variables supported:
  - `PORTAL_USER_<UNIVERSITY_SLUG>`
  - `PORTAL_PASS_<UNIVERSITY_SLUG>`
  - `EMAIL_<EMAIL_PASSWORD_REFERENCE>`
- Never commit real credentials.

## Known Limitations

1. Live screenshot streaming is event-driven checkpoint screenshots (not full video stream).
2. Desktop fallback requires Windows + `pywinauto` and a detectable native dialog title.
3. IMAP parsing is generic heuristic (subject/body/code/link extraction); some providers may need custom rules.
4. Recipe quality determines real-world success for each university portal.
5. In this repository environment, `.xlsx` sample generation may require local dependency install (CSV template is included).

