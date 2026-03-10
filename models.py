from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, HttpUrl, ConfigDict


class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class PageMetrics(BaseModel):
    url: str
    word_count: int
    h1_count: int
    h2_count: int
    h3_count: int
    cta_count: int
    internal_links: int
    external_links: int
    image_count: int
    images_missing_alt: int
    missing_alt_pct: float
    meta_title: str | None
    meta_description: str | None
    page_text: str  # truncated to first 3000 chars of visible body text


class Recommendation(BaseModel):
    priority: Priority
    recommendation: str
    reasoning: str


class AuditInsights(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    seo_analysis: str
    messaging_clarity: str
    cta_analysis: str
    content_depth: str
    ux_concerns: str
    recommendations: list[Recommendation]


class AuditResult(BaseModel):
    metrics: PageMetrics
    insights: AuditInsights
