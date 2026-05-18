import httpx
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Tags that usually contain the job description
CONTENT_TAGS = [
    {"id": "job-description"},
    {"class": "job-description"},
    {"class": "description"},
    {"class": "posting-description"},
    {"data-testid": "job-detail-description"},  # LinkedIn
    {"class": "show-more-less-html__markup"},    # LinkedIn fallback
]


def scrape_job(url: str, timeout: int = 10) -> tuple[str, str]:
    """
    Fetch a job posting page and extract its text content.

    Returns:
        (clean_text, page_title)

    Raises:
        ValueError: if page cannot be fetched or parsed
    """
    try:
        response = httpx.get(url, headers=HEADERS, timeout=timeout, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise ValueError(f"Could not fetch URL: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Try targeted selectors first
    for selector in CONTENT_TAGS:
        el = soup.find(attrs=selector)
        if el and len(el.get_text(strip=True)) > 100:
            return _clean(el.get_text(separator="\n")), _title(soup)

    # Fallback: biggest <article> or <main>
    for tag in ("article", "main", "section"):
        el = soup.find(tag)
        if el and len(el.get_text(strip=True)) > 200:
            return _clean(el.get_text(separator="\n")), _title(soup)

    # Last resort: strip everything, hope for the best
    body = soup.find("body")
    if body:
        text = _clean(body.get_text(separator="\n"))
        if len(text) > 200:
            return text[:6000], _title(soup)

    raise ValueError("Could not extract meaningful text from the page.")


def _clean(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    lines = [l for l in lines if l]          # drop blank lines
    deduped = []
    prev = None
    for line in lines:
        if line != prev:
            deduped.append(line)
        prev = line
    return "\n".join(deduped)[:6000]         # cap at 6k chars → ~1500 tokens


def _title(soup: BeautifulSoup) -> str:
    tag = soup.find("title")
    return tag.get_text(strip=True)[:120] if tag else "Unknown"
