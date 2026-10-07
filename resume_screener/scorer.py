"""Score and rank resumes against a job description."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .skills import find_skills

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3,4}\)?[\s-]?)\d{3}[\s-]?\d{3,4}")
YEARS_RE = re.compile(r"(\d{1,2})\+?\s*(?:years?|yrs?)\b(?:\s+of)?\s+(?:\w+\s+){0,3}experience", re.I)

#: Weight of semantic (TF-IDF) similarity vs. required-skill coverage.
DEFAULT_WEIGHTS = {"similarity": 0.4, "skills": 0.6}


@dataclass
class ScreeningResult:
    """The outcome of screening one resume."""

    name: str
    score: float
    similarity: float
    skill_coverage: float
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    email: str | None = None
    phone: str | None = None
    years_experience: int | None = None
    recommendation: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def extract_contact(text: str) -> tuple[str | None, str | None]:
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    return (email.group(0) if email else None, phone.group(0).strip() if phone else None)


def extract_years_experience(text: str) -> int | None:
    years = [int(m.group(1)) for m in YEARS_RE.finditer(text)]
    return max(years) if years else None


def recommend(score: float) -> str:
    if score >= 70:
        return "Strong match - shortlist"
    if score >= 45:
        return "Possible match - review"
    return "Weak match"


def tfidf_similarity(job_description: str, resumes: list[str]) -> list[float]:
    """Cosine similarity between the job description and each resume (0..1)."""
    if not resumes:
        return []
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    matrix = vectorizer.fit_transform([job_description, *resumes])
    return cosine_similarity(matrix[0:1], matrix[1:]).flatten().tolist()


def screen_resumes(
    job_description: str,
    resumes: dict[str, str],
    required_skills: list[str] | None = None,
    weights: dict[str, float] | None = None,
) -> list[ScreeningResult]:
    """Score every resume against the job description and return them best first.

    ``resumes`` maps a candidate name (usually the file name) to resume text.
    ``required_skills`` defaults to the skills detected in the job description.
    """
    if not job_description.strip():
        raise ValueError("Job description is empty")
    w = weights or DEFAULT_WEIGHTS
    required = sorted({s.lower() for s in required_skills} if required_skills else find_skills(job_description))
    names = list(resumes)
    sims = tfidf_similarity(job_description, [resumes[n] for n in names])

    results: list[ScreeningResult] = []
    for name, sim in zip(names, sims):
        text = resumes[name]
        found = find_skills(text)
        matched = [s for s in required if s in found]
        missing = [s for s in required if s not in found]
        coverage = len(matched) / len(required) if required else 0.0
        # TF-IDF cosine for resumes vs. a JD rarely exceeds ~0.5, so scale it up.
        sim_scaled = min(sim * 2, 1.0)
        score = round(100 * (w["similarity"] * sim_scaled + w["skills"] * coverage), 1)
        email, phone = extract_contact(text)
        results.append(
            ScreeningResult(
                name=name,
                score=score,
                similarity=round(sim, 4),
                skill_coverage=round(coverage, 4),
                matched_skills=matched,
                missing_skills=missing,
                email=email,
                phone=phone,
                years_experience=extract_years_experience(text),
                recommendation=recommend(score),
            )
        )
    return sorted(results, key=lambda r: r.score, reverse=True)
