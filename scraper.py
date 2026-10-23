import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

async def extract_website_content(url: str, session: aiohttp.ClientSession, max_chars: int = 1500) -> str:
    """Fetches URL and strips noise, keeping only high-signal content."""
    if not url.startswith("http"):
        url = "https://" + url

    try:
        async with session.get(url, headers=HEADERS, timeout=10) as resp:
            resp.raise_for_status()
            html = await resp.text()
    except Exception as err:
        return f"[SCRAPE_ERROR] {err}"

    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content elements
    for element in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "button"]):
        element.decompose()

    # Extract meta description
    meta_desc = ""
    meta = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    if meta and meta.get("content"):
        meta_desc = f"Meta Description: {meta['content'].strip()}\n"

    # Extract clean text
    raw_text = soup.get_text(separator=" ", strip=True)
    cleaned_text = re.sub(r"\s+", " ", raw_text)

    combined = f"{meta_desc}Content: {cleaned_text}"
    return combined[:max_chars].strip()

async def main():
    test_url = "https://resend.com"
    print(f"Testing scraper on {test_url}...\n")
    async with aiohttp.ClientSession() as session:
        content = await extract_website_content(test_url, session)
    print("--- EXTRACTED CONTENT ---")
    print(content[:400] + "...")

if __name__ == "__main__":
    asyncio.run(main())