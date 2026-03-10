import os
import json
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from models import PageMetrics, AuditInsights, AuditResult

LOG_FILE = Path("logs/prompt_log.json")

SYSTEM_PROMPT = """You are a website audit analyst for a digital marketing agency specializing in SEO, conversion optimization, and UX.

You will receive structured metrics scraped from a webpage along with a sample of its visible text content.

Your task is to return a JSON object with EXACTLY these keys:
- seo_analysis: string
- messaging_clarity: string
- cta_analysis: string
- content_depth: string
- ux_concerns: string
- recommendations: array of 3-5 objects, each with keys: priority (must be "High", "Medium", or "Low"), recommendation (string), reasoning (string)

Rules:
- Every insight MUST reference specific metric values from the data provided (e.g. "With 0 H2s and a word count of 312...")
- Be specific to this page. Do NOT give generic SEO advice.
- Insights should be actionable and relevant to a web marketing agency.
- Return ONLY valid JSON. No markdown code fences, no explanation outside the JSON object."""


def build_user_prompt(metrics: PageMetrics) -> str:
    return f"""Analyze the following webpage:

URL: {metrics.url}

EXTRACTED METRICS:
- Word count: {metrics.word_count}
- H1s: {metrics.h1_count} | H2s: {metrics.h2_count} | H3s: {metrics.h3_count}
- CTAs detected: {metrics.cta_count}
- Internal links: {metrics.internal_links} | External links: {metrics.external_links}
- Total images: {metrics.image_count} | Missing alt text: {metrics.images_missing_alt} ({metrics.missing_alt_pct}%)
- Meta title: {metrics.meta_title or "[None found]"}
- Meta description: {metrics.meta_description or "[None found]"}

PAGE TEXT SAMPLE (first 3000 chars):
{metrics.page_text}"""


def _log_prompt(url: str, user_prompt: str, raw_output: str, insights: AuditInsights) -> None:
    LOG_FILE.parent.mkdir(exist_ok=True)

    # Load existing logs or start fresh
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append({
        "timestamp": datetime.utcnow().isoformat(),
        "url": url,
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "raw_model_output": raw_output,
        "parsed_output": insights.model_dump()
    })

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def analyze(metrics: PageMetrics) -> AuditInsights:
    # Re-read .env on every call so key changes take effect without restart
    load_dotenv(override=True)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set. Add it to your .env file.")
    genai.configure(api_key=api_key)

    try:
        user_prompt = build_user_prompt(metrics)

        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=SYSTEM_PROMPT,
        )
        response = model.generate_content(user_prompt)
        raw_output = response.text.strip()

        # Gemini sometimes wraps JSON in ```json ... ``` despite being told not to
        if raw_output.startswith("```"):
            raw_output = raw_output.split("\n", 1)[-1]  # remove opening fence line
            raw_output = raw_output.rsplit("```", 1)[0].strip()  # remove closing fence

        try:
            insights = AuditInsights.model_validate_json(raw_output)
        except Exception:
            raise ValueError(f"Gemini returned invalid JSON: {raw_output[:200]}")

        _log_prompt(metrics.url, user_prompt, raw_output, insights)

        return insights

    except ValueError:
        raise
    except Exception:
        raise
