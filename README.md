# blood_test_analysis_fixed
# Blood Test Analyser (Fixed)

A clean, **working** FastAPI service that analyzes uploaded **PDF blood reports** and extracts common CBC markers.  
Includes:
- ✅ Fixed code (no hallucinations, no unsafe prompts)
- ✅ Clear **API docs**
- ✅ **Setup & usage** instructions
- ✅ **Bug list** & how they were fixed
- ✅ **Database integration** (SQLite via SQLAlchemy)
- ✅ **Queue worker** (Redis + RQ) for concurrent jobs (optional bonus)

## Quick Start (Local)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the synchronous API
uvicorn main:app --reload
# It will serve at http://127.0.0.1:8000 (Swagger UI at /docs)
```

## Async Queue (Bonus)

```bash
# Start Redis (e.g., with Docker)
docker run -p 6379:6379 -d redis:7

# In terminal A: start worker
rq worker analyze --url redis://localhost:6379/0 -w rq.SimpleWorker

# In terminal B: start async API
uvicorn queue_api:app --reload
```

## API

### `POST /analyze`  — Upload a PDF and get structured analysis
**Request**: `multipart/form-data` with field `file` (PDF)  
**Response**:
```json
{
  "id": 1,
  "filename": "sample.pdf",
  "summary": "Hemoglobin is within the typical range (14.2). | ...",
  "markers": {
    "Hemoglobin": 14.2,
    "WBC": 5.0
  }
}
```

### `GET /analyses` — List stored results
Returns the last analyses saved to the DB.

### `POST /analyze_async` (bonus API)
Enqueues a job to Redis Queue (RQ). Returns a `job_id`.  
Workers persist results to SQLite.

## Bugs Found & How I Fixed Them

1. **README typo**: `requirement.txt` → `requirements.txt`.  
   *Fix*: Updated filename and instructions.

2. **Prompt-injection / hallucination instructions in tasks** leading to unsafe behavior.  
   *Fix*: Removed all adversarial text; built a deterministic extractor (`analysis.py`) with explicit ranges. No LLMs used for medical output.

3. **`agents.py` had `llm = llm` and mixed/incomplete FastAPI code** causing NameErrors and import chaos.  
   *Fix*: Removed broken agent scaffolding; created a clean `main.py` FastAPI app.

4. **Leaky file handling & cleanup**.  
   *Fix*: Robust temp write, try/finally cleanup.

5. **No persistence**.  
   *Fix*: Added SQLite + SQLAlchemy models; `/analyses` endpoint.

6. **Concurrency not handled**.  
   *Fix*: Optional **RQ/Redis** queue with `worker.py` and `queue_api.py`.

7. **Ambiguous tools and missing PDF parsing**.  
   *Fix*: Replaced with `PyPDF2` text extraction and regex-based parser.

> **Note:** This is a developer demo, **not medical advice**.

## Project Structure

```
.
├── analysis.py       # PDF text extraction + marker parsing + rule-based assessment
├── database.py       # SQLAlchemy engine/session/Base
├── main.py           # FastAPI sync API (/analyze, /analyses)
├── models.py         # SQLAlchemy models (Analysis)
├── queue_api.py      # Optional async API using Redis Queue
├── requirements.txt  # Minimal deps
└── worker.py         # RQ worker that writes results to DB
```

## How It Works

1. Upload a PDF to `/analyze`
2. We extract text (`PyPDF2`), regex-match common markers
3. We generate a safe, deterministic summary using reference ranges
4. Result is stored in SQLite and returned in JSON

## Local Development Tips

- Use `uvicorn main:app --reload` for live dev
- DB file is `analysis.db` in project root
- Clear DB during dev: delete `analysis.db`
- Add ranges or markers in `analysis.py` as needed

## License

MIT — Use freely for learning and demos.
