"""FastAPI service: POST a job description and resume files, get a ranked shortlist."""

from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from . import __version__
from .parser import UnsupportedFileError, extract_text_from_bytes
from .scorer import screen_resumes

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_FILES = 50

app = FastAPI(
    title="AI Resume Screener",
    version=__version__,
    description="Rank resumes against a job description using TF-IDF similarity and skill matching.",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.post("/screen")
async def screen(
    job_description: str = Form(..., min_length=20),
    resumes: list[UploadFile] = File(...),
    required_skills: str | None = Form(None, description="Comma-separated skills"),
) -> dict:
    if len(resumes) > MAX_FILES:
        raise HTTPException(413, f"Upload at most {MAX_FILES} resumes at once")
    texts: dict[str, str] = {}
    for upload in resumes:
        data = await upload.read()
        if len(data) > MAX_FILE_BYTES:
            raise HTTPException(413, f"{upload.filename} is larger than 5 MB")
        try:
            texts[upload.filename or f"resume-{len(texts) + 1}"] = extract_text_from_bytes(data, upload.filename or "")
        except UnsupportedFileError as exc:
            raise HTTPException(415, str(exc)) from exc
    skills = [s.strip() for s in required_skills.split(",") if s.strip()] if required_skills else None
    results = screen_resumes(job_description, texts, skills)
    return {"count": len(results), "results": [r.to_dict() for r in results]}
