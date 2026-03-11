import pytest
import respx
from httpx import Response
from scraper import scrape_page

@respx.mock
def test_scrape_page_success():
    url = "https://example.com"
    mock_html = """
    <html>
        <head><title>Example Title</title><meta name="description" content="Example Description"></head>
        <body>
            <h1>Heading 1</h1>
            <h2>Heading 2</h2>
            <h3>Heading 3</h3>
            <a href="/internal">Internal</a>
            <a href="https://external.com">External</a>
            <img src="img1.jpg" alt="Alt 1">
            <img src="img2.jpg">
            <button>Click Here</button>
            <p>Some text content for word count calculation.</p>
        </body>
    </html>
    """
    respx.get(url).mock(return_value=Response(200, content=mock_html))
    
    metrics = scrape_page(url)
    
    assert metrics.url == url
    assert metrics.h1_count == 1
    assert metrics.h2_count == 1
    assert metrics.h3_count == 1
    assert metrics.internal_links == 1
    assert metrics.external_links == 1
    assert metrics.image_count == 2
    assert metrics.images_missing_alt == 1
    assert metrics.missing_alt_pct == 50.0
    assert metrics.meta_title == "Example Title"
    assert metrics.meta_description == "Example Description"
    assert "Heading 1" in metrics.page_text

@respx.mock
def test_scrape_page_error():
    url = "https://error.com"
    respx.get(url).mock(return_value=Response(404))
    
    with pytest.raises(Exception):
        scrape_page(url)
