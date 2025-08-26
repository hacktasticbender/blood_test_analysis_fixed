
from fastapi import FastAPI, File, UploadFile, HTTPException
import os, uuid
from redis import Redis
from rq import Queue

from .worker import analyze_pdf_job

app = FastAPI(title="Blood Test Analyser - Queue API", version="1.0.0")
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
conn = Redis.from_url(redis_url)
q = Queue("analyze", connection=conn)

@app.post("/analyze_async")
async def analyze_async(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    tmp_dir = "./uploads"
    os.makedirs(tmp_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tmp_dir, f"{file_id}-{file.filename}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    job = q.enqueue(analyze_pdf_job, file_path, file.filename)
    return {"job_id": job.get_id()}
