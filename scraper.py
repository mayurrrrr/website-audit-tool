import httpx
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from models import PageMetrics


CTA_KEYWORDS = [
    "get started", "contact", "buy", "sign up", "signup", "subscribe",
    "request", "download", "try", "learn more", "book", "schedule",
    "start", "join", "apply", "get a quote", "free trial", "demo"
]


def scrape_page(url: str) -> PageMetrics:
    """
    Fetch a URL and extract factual metrics from the page.
    Raises ValueError with a descriptive message if the page cannot be fetched.
    """
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AuditBot/1.0)"}

    try:
        response = httpx.get(url, follow_redirects=True, timeout=10, headers=headers)
    except httpx.ConnectError:
        raise ValueError(f"Could not connect to '{url}'. Check the URL is correct and the site is reachable.")
    except httpx.TimeoutException:
        raise ValueError(f"Request timed out after 10s. The site may be too slow or blocking scrapers.")
    except httpx.InvalidURL:
        raise ValueError(f"Invalid URL: '{url}'. Make sure it starts with https:// or http://")

    if response.status_code == 403:
        raise ValueError("Page blocked scraping (403). Try a different URL.")
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch page: HTTP {response.status_code}")


    soup = BeautifulSoup(response.text, "lxml")

    # Remove script, style, noscript tags before text extraction
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # --- Word count ---
    visible_text = soup.get_text(separator=" ", strip=True)
    word_count = len(visible_text.split())

    # --- Headings ---
    h1_count = len(soup.find_all("h1"))
    h2_count = len(soup.find_all("h2"))
    h3_count = len(soup.find_all("h3"))

    # --- CTAs ---
    button_count = len(soup.find_all("button"))
    cta_link_count = sum(
        1 for a in soup.find_all("a")
        if any(kw in a.get_text().strip().lower() for kw in CTA_KEYWORDS)
    )
    cta_count = button_count + cta_link_count

    # --- Links ---
    domain = urlparse(url).netloc
    internal_links = 0
    external_links = 0
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/") or domain in href:
            internal_links += 1
        elif href.startswith("http"):
            external_links += 1

    # --- Images ---
    imgs = soup.find_all("img")
    image_count = len(imgs)
    images_missing_alt = sum(
        1 for img in imgs
        if not img.get("alt") or img.get("alt", "").strip() == ""
    )
    if image_count > 0:
        missing_alt_pct = round((images_missing_alt / image_count) * 100, 1)
    else:
        missing_alt_pct = 0.0

    # --- Meta tags ---
    title_tag = soup.find("title")
    meta_title = title_tag.get_text(strip=True) if title_tag else None

    desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = desc_tag.get("content") if desc_tag else None

    # --- Page text (first 3000 chars) ---
    raw_text = " ".join(visible_text.split())
    page_text = raw_text[:3000]

    return PageMetrics(
        url=url,
        word_count=word_count,
        h1_count=h1_count,
        h2_count=h2_count,
        h3_count=h3_count,
        cta_count=cta_count,
        internal_links=internal_links,
        external_links=external_links,
        image_count=image_count,
        images_missing_alt=images_missing_alt,
        missing_alt_pct=missing_alt_pct,
        meta_title=meta_title,
        meta_description=meta_description,
        page_text=page_text,
    )
