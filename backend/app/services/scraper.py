"""Website ingestion: fetch → clean text → follow same-domain links (capped)."""
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "AI-Business-OS/1.0"}


def _clean(html: str) -> tuple[str, list[str]]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())
    links = [a.get("href") for a in soup.find_all("a", href=True)]
    return text, links


def scrape(url: str, max_pages: int = 5) -> str:
    base = urlparse(url).netloc
    seen, queue, texts = set(), [url], []
    with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        while queue and len(seen) < max_pages:
            current = queue.pop(0)
            if current in seen:
                continue
            seen.add(current)
            try:
                resp = client.get(current)
                text, links = _clean(resp.text)
                texts.append(f"[{current}]\n{text}")
                for link in links:
                    absolute = urljoin(current, link)
                    if urlparse(absolute).netloc == base and absolute not in seen:
                        queue.append(absolute)
            except httpx.HTTPError:
                continue
    return "\n\n".join(texts)
