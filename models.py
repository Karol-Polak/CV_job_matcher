from pydantic import BaseModel, HttpUrl
from typing import Optional


class AnalyzeRequest(BaseModel):
    cv_text: str
    job_url: Optional[str] = None
    job_text: Optional[str] = None  # fallback if URL scraping fails

    model_config = {
        "json_schema_extra": {
            "example": {
                "cv_text": "Python developer with 3 years experience...",
                "job_url": "https://example.com/job/python-developer",
            }
        }
    }


class MatchResult(BaseModel):
    match_score: int                  # 0–100
    grade: str                        # A / B / C / D
    strengths: list[str]              # what already matches
    missing_keywords: list[str]       # skills/keywords absent in CV
    improvements: list[str]           # concrete CV edit suggestions
    summary: str                      # 2-3 sentence human-readable verdict


class AnalyzeResponse(BaseModel):
    job_title: str
    company: Optional[str]
    result: MatchResult
    job_text_preview: str             # first 300 chars of scraped job
