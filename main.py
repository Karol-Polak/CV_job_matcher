from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import AnalyzeRequest, AnalyzeResponse
from scraper import scrape_job
from analyzer import analyze


app = FastAPI(
    title="CV Job Matcher",
    description="Paste your CV + a job URL → get an AI-powered match score and improvement tips.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_cv(request: AnalyzeRequest):
    """
    Analyze CV vs job posting.

    Provide either `job_url` (preferred) or `job_text` directly.
    """
    # Get job text
    if request.job_url:
        try:
            job_text, page_title = scrape_job(str(request.job_url))
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
    elif request.job_text:
        job_text = request.job_text
        page_title = "Provided directly"
    else:
        raise HTTPException(
            status_code=422,
            detail="Provide either job_url or job_text."
        )

    #Run LLM analysis
    try:
        result, job_title, company = analyze(request.cv_text, job_text)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    #Return response
    return AnalyzeResponse(
        job_title=job_title,
        company=company,
        result=result,
        job_text_preview=job_text[:300] + "..." if len(job_text) > 300 else job_text,
    )
