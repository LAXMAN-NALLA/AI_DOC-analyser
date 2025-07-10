# main.py
import os
import tempfile
import logging
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from textract_service import extract_text
from openai_service import analyze_document

app = FastAPI()
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".docx", ".csv", ".png", ".jpg", ".jpeg"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        logging.info(f"Processing file: {file.filename}")
        extracted_text = await extract_text(tmp_path, ext)
        if not extracted_text.strip():
            raise HTTPException(status_code=422, detail="Failed to extract text from document")

        analysis_result = await analyze_document(extracted_text)
        return {
            "filename": file.filename,
            "filesize_kb": round(os.path.getsize(tmp_path) / 1024, 2),
            "analysis": analysis_result
        }
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception as cleanup_error:
            logging.warning(f"Failed to delete temporary file: {cleanup_error}")
