# Website Audit Tool

An AI-powered website audit tool built with Python + Streamlit. Accepts a single URL, scrapes factual metrics, sends them to Google Gemini for structured AI analysis, and displays both in a polished Streamlit UI.

---

## Architecture Overview

```
website-audit-tool/
├── app.py           # Streamlit UI — input, results display
├── scraper.py       # Fetches URL with httpx, parses HTML with BeautifulSoup
├── ai_analyzer.py   # Builds prompts, calls Gemini API, logs every call
├── models.py        # Pydantic v2 models (PageMetrics, AuditInsights, etc.)
├── logs/
│   └── prompt_log.json   # Append-only log of every Gemini API call
├── .streamlit/
│   └── config.toml       # Dark-theme Streamlit configuration
├── requirements.txt
├── .env.example
└── .gitignore
```

**Strict separation of concerns:**
- `scraper.py` only fetches and parses — no AI, no UI
- `ai_analyzer.py` only builds prompts and calls Gemini — no HTTP fetching, no UI
- `models.py` only defines Pydantic models — no logic
- `app.py` only renders UI — calls the other two layers

---

## AI Design Decisions

- **Model:** `gemini-flash-latest` — fast, cost-effective, strong at structured JSON output
- **Output format:** Raw JSON string, fence-stripped then parsed with `AuditInsights.model_validate_json()` — Gemini occasionally wraps output in ` ```json ``` ` fences despite instruction; the code strips these before parsing
- **System prompt:** Passed via `system_instruction` parameter — instructs Gemini to ONLY return valid JSON, reference specific metric values, and avoid generic advice
- **Logging:** Every API call (system prompt, user prompt, raw output, parsed result) is appended to `logs/prompt_log.json` for auditability and debugging

---

## Trade-offs Made

| Decision | Trade-off |
|---|---|
| `httpx` (sync) instead of async | Simpler Streamlit integration; async adds complexity without benefit here |
| Page text truncated to 3000 chars | Keeps Gemini token usage predictable; misses content below the fold |
| CTA detection via keyword matching | Fast and dependency-free; not pixel-perfect (misses image-only CTAs) |
| Single page analysis only | Sufficient for scoping the tool; crawling adds significant complexity |
| Structured JSON output from Gemini | Reliable parsing; requires strict system prompt, fence-stripping, and error handling |

---

## What I'd Improve With More Time

1. **JavaScript-rendered pages** — Add Playwright support for SPAs (React, Vue, Angular)
2. **Async scraping** — Use `httpx.AsyncClient` for concurrent multi-page audits
3. **Smarter CTA detection** — CSS class / aria-role analysis beyond keyword matching
4. **Core Web Vitals** — Integrate Lighthouse or PageSpeed Insights API
5. **Export to PDF/CSV** — Let users download the audit report
6. **Caching** — `@st.cache_data` on scrape results to avoid redundant fetches during a session
7. **Token-aware truncation** — Use tiktoken to truncate page text by tokens, not characters

---

## Local Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd website-audit-tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY (get one free at aistudio.google.com)

# 4. Run the app
streamlit run app.py
```

---

## Known Limitations

- `httpx` cannot execute JavaScript — React/Vue/Angular SPAs will return empty or minimal content
- CTA detection is heuristic (keyword matching on link/button text) — not pixel-perfect
- Single page analysis only — no crawling
- Page text truncated to 3000 chars to manage Gemini token usage
- Some sites block bots even with a User-Agent header (Cloudflare, etc.)

---

## Sample Log Output

Every audit is appended to `logs/prompt_log.json`. Here's a trimmed example from a real run against `ycombinator.com`:

```json
{
  "timestamp": "2026-03-10T18:05:19.221446",
  "url": "https://www.ycombinator.com/",
  "system_prompt": "You are a website audit analyst...",
  "user_prompt": "Analyze the following webpage:\n\nURL: https://www.ycombinator.com/\n\nEXTRACTED METRICS:\n- Word count: 1580\n- H1s: 0 | H2s: 6 | H3s: 11\n- CTAs detected: 28\n...",
  "raw_model_output": "{\"seo_analysis\": \"The page is missing an H1...\", ...}",
  "parsed_output": {
    "seo_analysis": "The page is missing an H1, which is a critical on-page SEO element. The meta title is simply 'Y Combinator,' which is generic and doesn't include relevant keywords.",
    "messaging_clarity": "The messaging focuses on showcasing successful companies. While this highlights success stories, more direct explanation of the program's benefits might improve clarity.",
    "cta_analysis": "The page has 28 CTAs, primarily focused on 'Apply.' While having clear calls to action is good, the sheer volume might overwhelm users.",
    "content_depth": "With a word count of 1580 and 6 H2s, the page provides a good amount of content but primarily focuses on social proof. Consider adding more in-depth explanations of the YC program.",
    "ux_concerns": "The high number of CTAs (28) could be overwhelming. Although there are 85 images and no missing alt text, consider optimizing image file sizes for page load speed.",
    "recommendations": [
      {
        "priority": "High",
        "recommendation": "Add an H1 tag incorporating relevant keywords such as 'startup accelerator' or 'seed funding'.",
        "reasoning": "The absence of an H1 tag negatively impacts SEO and reduces the page's topical relevance."
      },
      {
        "priority": "Medium",
        "recommendation": "Refine the meta title to be more specific and keyword-rich.",
        "reasoning": "A targeted meta title improves click-through rates from SERPs and attracts more relevant traffic."
      }
    ]
  }
}
```

---

## Deployed App

🚀 **Live Link:** [website-audit-tool-mayur.streamlit.app](https://website-audit-tool-mayur.streamlit.app/)

> _Deployed via Streamlit Community Cloud._
