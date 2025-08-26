
import os, json, uuid
from rq import Queue, Connection, Worker
from redis import Redis
from typing import Dict, Tuple

from .database import Base, engine, SessionLocal
from .models import Analysis
from .analysis import extract_text_from_pdf, parse_markers, analyze_markers

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
conn = Redis.from_url(redis_url)

def analyze_pdf_job(path: str, orig_filename: str) -> int:
    text = extract_text_from_pdf(path)
    markers = parse_markers(text)
    summary, markers_found = analyze_markers(markers)
    db = SessionLocal()
    rec = Analysis(filename=orig_filename, summary=summary, markers_json=json.dumps(markers_found))
    db.add(rec)
    db.commit()
    db.refresh(rec)
    db.close()
    return rec.id

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    with Connection(conn):
        worker = Worker(["analyze"])
        worker.work()
