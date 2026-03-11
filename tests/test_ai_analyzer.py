import pytest
from unittest.mock import MagicMock, patch
from ai_analyzer import analyze
from models import PageMetrics, AuditInsights, Priority

def test_analyze_success(sample_metrics):
    # Mocking genai.GenerativeModel
    mock_response = MagicMock()
    mock_response.text = """
    {
        "seo_analysis": "Test SEO analysis.",
        "messaging_clarity": "Test messaging clarity.",
        "cta_analysis": "Test CTA analysis.",
        "content_depth": "Test content depth.",
        "ux_concerns": "Test UX concerns.",
        "recommendations": [
            {
                "priority": "High",
                "recommendation": "Improve SEO.",
                "reasoning": "Reasoning here."
            }
        ]
    }
    """
    
    with patch("google.generativeai.GenerativeModel") as MockModel:
        instance = MockModel.return_value
        instance.generate_content.return_value = mock_response
        
        # Mock _log_prompt to avoid file I/O errors and log pollution
        with patch("ai_analyzer._log_prompt") as mock_log:
            # We also need to mock os.getenv to return a dummy key
            with patch("os.getenv", return_value="dummy_key"):
                insights = analyze(sample_metrics)
                
                assert isinstance(insights, AuditInsights)
                assert insights.seo_analysis == "Test SEO analysis."
                assert len(insights.recommendations) == 1
                assert insights.recommendations[0].priority == Priority.HIGH
                # Verify that it was called
                instance.generate_content.assert_called_once()

def test_analyze_invalid_json(sample_metrics):
    mock_response = MagicMock()
    mock_response.text = "Invalid JSON string"
    
    with patch("google.generativeai.GenerativeModel") as MockModel:
        instance = MockModel.return_value
        instance.generate_content.return_value = mock_response
        
        with patch("os.getenv", return_value="dummy_key"):
            with pytest.raises(ValueError, match="Gemini returned invalid JSON"):
                analyze(sample_metrics)

def test_analyze_missing_api_key(sample_metrics):
    with patch("os.getenv", return_value=None):
        with pytest.raises(ValueError, match="GOOGLE_API_KEY is not set"):
            analyze(sample_metrics)
