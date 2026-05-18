import pytest
from unittest.mock import patch, MagicMock

from analyzer import analyze, _safe_parse
from models import MatchResult


#_safe_parse
def test_safe_parse_clean_json():
    raw = '{"match_score": 75, "grade": "B", "job_title": "Dev", "company": "Acme", "strengths": [], "missing_keywords": [], "improvements": [], "summary": "Good fit."}'
    result = _safe_parse(raw)
    assert result["match_score"] == 75


def test_safe_parse_strips_markdown_fences():
    raw = '```json\n{"match_score": 80, "grade": "A", "job_title": "Dev", "company": null, "strengths": [], "missing_keywords": [], "improvements": [], "summary": "Great."}\n```'
    result = _safe_parse(raw)
    assert result["grade"] == "A"


def test_safe_parse_invalid_json_raises():
    with pytest.raises(ValueError, match="invalid JSON"):
        _safe_parse("this is not json at all")


#analyze (mocked LLM)
MOCK_RESPONSE_JSON = """{
  "match_score": 82,
  "grade": "A",
  "job_title": "Python Backend Developer",
  "company": "TechCorp",
  "strengths": ["Python experience", "FastAPI knowledge", "REST API design"],
  "missing_keywords": ["Docker", "Kubernetes"],
  "improvements": [
    "Add Docker to skills section",
    "Mention any CI/CD experience in job descriptions"
  ],
  "summary": "Strong candidate. Missing some DevOps tooling but core Python skills are a solid match."
}"""


def _mock_message():
    msg = MagicMock()
    msg.content = [MagicMock(text=MOCK_RESPONSE_JSON)]
    return msg


@patch("analyzer.CLIENT")
def test_analyze_returns_match_result(mock_client):
    mock_client.messages.create.return_value = _mock_message()

    result, job_title, company = analyze(
        cv_text="Python developer with FastAPI experience.",
        job_text="We need a Python Backend Developer with Docker skills.",
    )

    assert isinstance(result, MatchResult)
    assert result.match_score == 82
    assert result.grade == "A"
    assert "Docker" in result.missing_keywords
    assert job_title == "Python Backend Developer"
    assert company == "TechCorp"


@patch("analyzer.CLIENT")
def test_analyze_score_clamped_to_int(mock_client):
    mock_client.messages.create.return_value = _mock_message()
    result, _, _ = analyze("cv", "job")
    assert isinstance(result.match_score, int)


#MatchResult validation
def test_match_result_schema():
    r = MatchResult(
        match_score=55,
        grade="C",
        strengths=["Python"],
        missing_keywords=["Kubernetes"],
        improvements=["Add K8s experience"],
        summary="Decent fit.",
    )
    assert r.match_score == 55
    assert r.grade == "C"
