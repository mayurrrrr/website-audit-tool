import streamlit as st
from scraper import scrape_page
from ai_analyzer import analyze
from models import AuditResult

# Must be the very first Streamlit call
st.set_page_config(
    page_title="Website Audit Tool",
    page_icon="🔍",
    layout="wide"
)

# Load custom CSS
st.markdown("""
<style>
    .metric-card {
        background: #1E293B;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .insight-card {
        background: #1E293B;
        border-left: 4px solid #2563EB;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .rec-card {
        background: #1E293B;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .badge-high { background: #DC2626; color: white; padding: 2px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
    .badge-medium { background: #D97706; color: white; padding: 2px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
    .badge-low { background: #16A34A; color: white; padding: 2px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
    .muted { color: #94A3B8; font-size: 0.9rem; }
    h1 { text-align: center; }
    .subtitle { text-align: center; color: #94A3B8; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🔍 Website Audit Tool")
st.markdown('<p class="subtitle">AI-powered page analysis for SEO, messaging, and UX</p>', unsafe_allow_html=True)

# URL Input — centered in middle column
_, col_mid, _ = st.columns([1, 2, 1])
with col_mid:
    url_input = st.text_input("", placeholder="https://example.com", label_visibility="collapsed")
    run_audit = st.button("Run Audit", type="primary", use_container_width=True)


def _render_results(result: AuditResult) -> None:
    """Render the full audit results: metrics + AI insights + recommendations."""

    # --- Section 1: Two columns ---
    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.subheader("📊 Factual Metrics")

        # Metric tiles in a 3-column sub-grid
        m = result.metrics
        r1c1, r1c2, r1c3 = st.columns(3)
        r1c1.metric("Word Count", m.word_count)
        r1c2.metric("H1", m.h1_count)
        r1c3.metric("H2", m.h2_count)

        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.metric("H3", m.h3_count)
        r2c2.metric("CTAs", m.cta_count)
        r2c3.metric("Internal Links", m.internal_links)

        r3c1, r3c2, r3c3 = st.columns(3)
        r3c1.metric("External Links", m.external_links)
        r3c2.metric("Images", m.image_count)
        r3c3.metric("Missing Alt Text", f"{m.images_missing_alt} ({m.missing_alt_pct}%)")

        # Missing alt text alert
        if m.images_missing_alt == 0:
            st.success("✅ All images have alt text")
        elif m.missing_alt_pct > 30:
            st.warning(f"⚠️ {m.missing_alt_pct}% of images are missing alt text")

        # Meta title
        st.markdown("**Meta Title**")
        if m.meta_title:
            st.write(m.meta_title)
        else:
            st.markdown('<span style="color:#EF4444;">⚠️ None found</span>', unsafe_allow_html=True)

        # Meta description
        st.markdown("**Meta Description**")
        if m.meta_description:
            st.write(m.meta_description)
        else:
            st.markdown('<span style="color:#EF4444;">⚠️ None found</span>', unsafe_allow_html=True)

    with col_right:
        st.subheader("🤖 AI Insights")
        ins = result.insights

        insights_data = [
            ("🔍 SEO Structure", ins.seo_analysis),
            ("💬 Messaging Clarity", ins.messaging_clarity),
            ("📣 CTA Usage", ins.cta_analysis),
            ("📄 Content Depth", ins.content_depth),
            ("🖥️ UX Concerns", ins.ux_concerns),
        ]

        for label, text in insights_data:
            st.markdown(
                f'<div class="insight-card"><strong>{label}</strong><br>{text}</div>',
                unsafe_allow_html=True
            )

    # --- Section 2: Recommendations (full width) ---
    st.divider()
    st.subheader("✅ Prioritized Recommendations")

    badge_map = {
        "High": "badge-high",
        "Medium": "badge-medium",
        "Low": "badge-low",
    }

    for rec in result.insights.recommendations:
        badge_class = badge_map.get(rec.priority.value, "badge-low")
        st.markdown(
            f"""<div class="rec-card">
                <span class="{badge_class}">{rec.priority.value}</span>
                <br><br>
                <strong>{rec.recommendation}</strong>
                <p class="muted">{rec.reasoning}</p>
            </div>""",
            unsafe_allow_html=True
        )


# --- Audit flow ---
if run_audit and url_input:
    with st.spinner("Scraping page and running AI analysis..."):
        try:
            metrics = scrape_page(url_input)
            insights = analyze(metrics)
            result = AuditResult(metrics=metrics, insights=insights)
            _render_results(result)
        except ValueError as e:
            st.error(f"❌ {str(e)}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
elif run_audit and not url_input:
    st.warning("⚠️ Please enter a URL")
