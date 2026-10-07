"""AI Resume Screener: rank resumes against a job description."""

from .parser import extract_text
from .scorer import ScreeningResult, screen_resumes

__all__ = ["extract_text", "screen_resumes", "ScreeningResult"]
__version__ = "1.0.0"
