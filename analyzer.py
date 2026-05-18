import json
import re
import anthropic

from models import MatchResult


CLIENT = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
MODEL = "claude-3-5-haiku-20241022"

SYSTEM_PROMPT = """You are an expert technical recruiter and career coach.
Your job is to compare a candidate's CV against a job posting and return a structured JSON analysis.

Rules:
- Be honest and specific – vague feedback is useless.
- missing_keywords: only real skill/tool gaps, not soft skills.
- improvements: actionable edits the candidate can make TODAY (e.g. "Add FastAPI to skills section").
- match_score: 0-100 integer reflecting genuine fit (not inflated).
- grade: A (80-100), B (60-79), C (40-59), D (0-39).
- All text fields must be in the same language as the CV.
- Return ONLY valid JSON, no markdown, no explanation."""

ANALYSIS_PROMPT = """Analyze the fit between this CV and job posting.

=== CV ===
{cv_text}

=== JOB POSTING ===
{job_text}

Return this exact JSON structure:
{{
  "match_score": <integer 0-100>,
  "grade": "<A|B|C|D>",
  "job_title": "<extracted job title>",
  "company": "<extracted company name or null>",
  "strengths": ["<strength 1>", "<strength 2>", ...],
  "missing_keywords": ["<keyword 1>", "<keyword 2>", ...],
  "improvements": ["<concrete suggestion 1>", "<concrete suggestion 2>", ...],
  "summary": "<2-3 sentence verdict>"
}}"""


def analyze(cv_text: str, job_text: str) -> tuple[MatchResult, str, str | None]:
    """
    Send CV + job text to the LLM and parse the structured response.

    Returns:
        (MatchResult, job_title, company)
    """
    prompt = ANALYSIS_PROMPT.format(
        cv_text=cv_text.strip()[:4000],   # cap CV at ~1k tokens
        job_text=job_text.strip()[:4000],  # cap job at ~1k tokens
    )

    message = CLIENT.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    data = _safe_parse(raw)

    result = MatchResult(
        match_score=int(data.get("match_score", 0)),
        grade=data.get("grade", "D"),
        strengths=data.get("strengths", []),
        missing_keywords=data.get("missing_keywords", []),
        improvements=data.get("improvements", []),
        summary=data.get("summary", ""),
    )

    return result, data.get("job_title", "Unknown position"), data.get("company")


def _safe_parse(text: str) -> dict:
    """Parse JSON, stripping markdown fences if present."""
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}\n\nRaw output:\n{text}")
