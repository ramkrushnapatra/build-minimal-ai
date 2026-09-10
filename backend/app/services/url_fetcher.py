from __future__ import annotations

import logging
import re

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

MAX_CONTENT_LENGTH = 50000
TIMEOUT_SECONDS = 15


async def fetch_url_content(url: str) -> tuple[str, str]:
    """Fetch a URL and return (title, plain text content)."""
    logger.info("Fetching URL: %s", url)
    async with httpx.AsyncClient(follow_redirects=True, timeout=TIMEOUT_SECONDS) as client:
        response = await client.get(url, headers={"User-Agent": "build-minimal-ai/0.1"})
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else url
    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if len(text) > MAX_CONTENT_LENGTH:
        text = text[:MAX_CONTENT_LENGTH]

    if not text:
        raise ValueError("No readable text found at URL")

    logger.info("Fetched %d chars from %s", len(text), url)
    return title, text
