import pytest
from src.core.export.charts import ChartGenerator

def test_pie_chart_generation():
    """Test generating a pie chart SVG."""
    data = {
        'Critical': 5,
        'High': 10,
        'Medium': 15,
        'Low': 20
    }
    svg = ChartGenerator.generate_pie_chart(data, "Severity Distribution")

    assert svg.startswith('<svg')
    assert 'Severity Distribution' in svg
    assert 'Critical (5)' in svg
    assert 'High (10)' in svg
    assert 'Medium (15)' in svg
    assert 'Low (20)' in svg
    assert 'fill="#e53e3e"' in svg  # Critical color

def test_bar_chart_generation():
    """Test generating a bar chart SVG."""
    data = {
        'src/main.py': 10,
        'src/utils.py': 5,
        'src/core.py': 2
    }
    svg = ChartGenerator.generate_bar_chart(data, "Top Violations")

    assert svg.startswith('<svg')
    assert 'Top Violations' in svg
    assert 'src/main.py' in svg
    assert '10' in svg
    assert 'src/utils.py' in svg
    assert '5' in svg
    assert 'src/core.py' in svg
    assert '2' in svg

def test_empty_charts():
    """Test charts with empty data."""
    svg_pie = ChartGenerator.generate_pie_chart({}, "Empty Pie")
    assert 'No Data Available' in svg_pie

    svg_bar = ChartGenerator.generate_bar_chart({}, "Empty Bar")
    assert 'No Data Available' in svg_bar

def test_zero_sum_pie_chart():
    """Test pie chart with zero sum."""
    data = {'Critical': 0, 'High': 0}
    svg = ChartGenerator.generate_pie_chart(data, "Zero Sum")
    assert 'No Data Available' in svg

def test_bar_chart_truncation():
    """Test label truncation in bar chart."""
    long_label = "src/very/long/path/that/should/be/truncated/file.py"
    data = {long_label: 5}
    svg = ChartGenerator.generate_bar_chart(data, "Truncation Test")

    # Check if truncated label exists in SVG
    truncated = long_label[:22] + "..."
    assert truncated in svg
    assert "..." in svg

def test_xss_prevention():
    """Test that labels are escaped to prevent XSS."""
    malicious_label = "<script>alert('xss')</script>"
    data = {malicious_label: 10}
    svg = ChartGenerator.generate_bar_chart(data, "XSS Test")

    # Ensure raw script tag is NOT present.
    # The label will likely be truncated due to length, but we verify
    # it doesn't contain the raw malicious tag.
    assert "<script>" not in svg
    assert "&lt;" in svg or "..." in svg
