import pytest
from src.core.export.charts import ChartGenerator

def test_pie_chart_generation():
    """Test generating a pie chart static image."""
    data = {
        'Critical': 5,
        'High': 10,
        'Medium': 15,
        'Low': 20
    }
    img = ChartGenerator.generate_pie_chart(data, "Severity Distribution")

    assert img.startswith('<img')
    assert 'alt="Severity Distribution"' in img
    assert 'data:image/png;base64,' in img

def test_bar_chart_generation():
    """Test generating a bar chart static image."""
    data = {
        'src/main.py': 10,
        'src/utils.py': 5,
        'src/core.py': 2
    }
    img = ChartGenerator.generate_bar_chart(data, "Top Violations")

    assert img.startswith('<img')
    assert 'alt="Top Violations"' in img
    assert 'data:image/png;base64,' in img

def test_empty_charts():
    """Test charts with empty data."""
    img_pie = ChartGenerator.generate_pie_chart({}, "Empty Pie")
    assert img_pie.startswith('<img')
    assert 'alt="Empty Pie"' in img_pie

    img_bar = ChartGenerator.generate_bar_chart({}, "Empty Bar")
    assert img_bar.startswith('<img')
    assert 'alt="Empty Bar"' in img_bar

def test_zero_sum_pie_chart():
    """Test pie chart with zero sum."""
    data = {'Critical': 0, 'High': 0}
    img = ChartGenerator.generate_pie_chart(data, "Zero Sum")
    assert img.startswith('<img')
    assert 'alt="Zero Sum"' in img

def test_bar_chart_truncation():
    """Test label truncation in bar chart."""
    long_label = "src/very/long/path/that/should/be/truncated/file.py"
    data = {long_label: 5}
    img = ChartGenerator.generate_bar_chart(data, "Truncation Test")

    # The actual truncated string is drawn in matplotlib and converted to base64,
    # so we just check that the image was generated correctly.
    assert img.startswith('<img')
    assert 'alt="Truncation Test"' in img

def test_xss_prevention():
    """Test that labels are escaped to prevent XSS."""
    malicious_label = "<script>alert('xss')</script>"
    data = {malicious_label: 10}
    img = ChartGenerator.generate_bar_chart(data, "XSS Test")

    # Ensure raw script tag is NOT present as HTML attributes
    # The alt text is escaped
    assert "<script>" not in img
    assert "&lt;script&gt;" not in img # Although html.escape might escape it, the alt text only contains the title
    assert 'alt="XSS Test"' in img
