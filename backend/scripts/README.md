# Backend scripts

Utility and test scripts for the VIRO-AI backend. Run from the **backend** directory so that `app` imports work.

- **check_project_status.py** – Check status of latest SARS-CoV-2 project in DB (uses repo-root `Viroai_DataBase/viroai.db`).
- **fix_store_results.py** – Placeholder/notes for store-results fix.
- **measure_processing_time.py** – Measure ML processing time for a project (requires backend on PYTHONPATH).
- **test_*.py** – API/auth/project flow tests (hit `http://localhost:8000`).

Example (from repo root):

```bash
cd backend
python scripts/check_project_status.py
python scripts/measure_processing_time.py
python scripts/test_simple_flow.py
```
