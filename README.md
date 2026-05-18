# CV Job Matcher

AI-powered tool that compares your CV against a job posting and returns a structured match score with actionable improvement tips.

**Paste your CV + a job URL → get a score, gap analysis, and concrete edits in seconds.**

---

## Features

- **Match score (0–100)** with letter grade (A/B/C/D)
- **Strengths** – what already matches the job requirements
- **Missing keywords** – skills/tools absent from your CV
- **Improvement suggestions** – concrete, actionable CV edits
- **Works with any language** – response language follows your CV
- Scrapes job postings automatically from URL (LinkedIn, NoFluffJobs, etc.)
- Clean REST API built with FastAPI + interactive docs at `/docs`

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI, Pydantic v2 |
| AI | Anthropic Claude (claude-3-5-haiku) |
| Scraping | httpx, BeautifulSoup4 |
| Testing | pytest, unittest.mock |

---

## Quickstart

```bash
# 1. Clone & install
git clone https://github.com/Karol-Polak/cv-job-matcher.git
cd cv-job-matcher
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Run
uvicorn main:app --reload
```

Open **http://localhost:8000/docs** for the interactive API explorer.

---

## API

### `POST /analyze`

```json
{
  "cv_text": "Your full CV text here...",
  "job_url": "https://example.com/job/python-developer"
}
```

**Response:**

```json
{
  "job_title": "Python Backend Developer",
  "company": "TechCorp",
  "result": {
    "match_score": 78,
    "grade": "B",
    "strengths": [
      "Strong Python experience",
      "FastAPI matches the required framework",
      "REST API design experience"
    ],
    "missing_keywords": ["Docker", "Kubernetes", "Redis"],
    "improvements": [
      "Add Docker to your skills section – it appears 4 times in the job posting",
      "Mention any experience with containerization or deployment in your job descriptions",
      "Add a line about working with caching layers if applicable"
    ],
    "summary": "Good overall fit. Core Python and API skills align well. The main gap is DevOps tooling (Docker/K8s) which appears prominently in the requirements."
  },
  "job_text_preview": "We are looking for a Python Backend Developer..."
}
```

You can also pass `job_text` directly instead of `job_url` if the page can't be scraped:

```json
{
  "cv_text": "...",
  "job_text": "Full job description text pasted here..."
}
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use mocked LLM responses – no API key required to run them.

---

## Project Structure

```
cv-job-matcher/
├── main.py          # FastAPI app & routes
├── analyzer.py      # LLM integration & prompt engineering
├── scraper.py       # Job posting fetcher (httpx + BeautifulSoup)
├── models.py        # Pydantic request/response schemas
├── tests/
│   └── test_analyzer.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Roadmap

- [ ] PDF CV upload support
- [ ] Batch analysis (compare one CV against multiple jobs)
- [ ] Simple web UI
- [ ] Support for more job boards (Indeed, Glassdoor)


