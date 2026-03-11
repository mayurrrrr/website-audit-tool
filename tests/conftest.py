import pytest
from models import PageMetrics, Priority, Recommendation, AuditInsights

@pytest.fixture
def sample_metrics():
    return PageMetrics(
        url="https://example.com",
        word_count=500,
        h1_count=1,
        h2_count=2,
        h3_count=3,
        cta_count=5,
        internal_links=10,
        external_links=5,
        image_count=4,
        images_missing_alt=2,
        missing_alt_pct=50.0,
        meta_title="Example Title",
        meta_description="Example Description",
        page_text="This is some sample text from the page."
    )

@pytest.fixture
def sample_insights():
    return AuditInsights(
        seo_analysis="Good SEO.",
        messaging_clarity="Clear messaging.",
        cta_analysis="Effective CTAs.",
        content_depth="Deep content.",
        ux_concerns="Minimal UX concerns.",
        recommendations=[
            Recommendation(
                priority=Priority.HIGH,
                recommendation="Improve alt text.",
                reasoning="Many images are missing alt text."
            )
        ]
    )
