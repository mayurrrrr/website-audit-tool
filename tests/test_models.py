from models import PageMetrics, Priority, Recommendation, AuditInsights
import pytest

def test_page_metrics_creation():
    metrics = PageMetrics(
        url="https://test.com",
        word_count=100,
        h1_count=1,
        h2_count=2,
        h3_count=3,
        cta_count=4,
        internal_links=5,
        external_links=6,
        image_count=7,
        images_missing_alt=8,
        missing_alt_pct=0.5,
        meta_title="Title",
        meta_description="Desc",
        page_text="Text"
    )
    assert metrics.url == "https://test.com"
    assert metrics.word_count == 100

def test_recommendation_creation():
    rec = Recommendation(
        priority=Priority.HIGH,
        recommendation="Do something",
        reasoning="Because"
    )
    assert rec.priority == Priority.HIGH
    assert rec.recommendation == "Do something"

def test_audit_insights_creation():
    insights = AuditInsights(
        seo_analysis="SEO",
        messaging_clarity="Clarity",
        cta_analysis="CTA",
        content_depth="Depth",
        ux_concerns="UX",
        recommendations=[]
    )
    assert insights.seo_analysis == "SEO"
    assert insights.recommendations == []
