
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os, uuid, json

from .database import Base, engine, SessionLocal
from .models import Analysis
from .analysis import extract_text_from_pdf, parse_markers, analyze_markers

app = FastAPI(title="Blood Test Analyser", version="1.0.0")

# Create DB tables
Base.metadata.create_all(bind=engine)

class AnalysisOut(BaseModel):
    id: int
    filename: str
    summary: str
    markers: dict

    class Config:
        from_attributes = True

@app.post("/analyze", response_model=AnalysisOut)
async def analyze(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    tmp_dir = "./uploads"
    os.makedirs(tmp_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tmp_dir, f"{file_id}-{file.filename}")

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        text = extract_text_from_pdf(file_path)
        markers = parse_markers(text)
        summary, markers_found = analyze_markers(markers)

        # Save to DB
        db = SessionLocal()
        record = Analysis(
            filename=file.filename,
            summary=summary,
            markers_json=json.dumps(markers_found),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        db.close()

        return AnalysisOut(
            id=record.id,
            filename=record.filename,
            summary=record.summary,
            markers=markers_found,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

@app.get("/analyses", response_model=list[AnalysisOut])
def list_analyses():
    db = SessionLocal()
    rows = db.query(Analysis).order_by(Analysis.id.desc()).all()
    out = [
        AnalysisOut(
            id=r.id, filename=r.filename, summary=r.summary, markers=json.loads(r.markers_json)
        )
        for r in rows
    ]
    db.close()
    return out
