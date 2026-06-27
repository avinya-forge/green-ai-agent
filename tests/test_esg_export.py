import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

from src.core.export.esg_exporter import ESGExporter

@pytest.fixture
def mock_results():
    return {
        'issues': [
            {'severity': 'critical', 'tags': ['security']},
            {'severity': 'high', 'tags': ['secret', 'security']},
            {'severity': 'minor', 'tags': ['performance']}
        ],
        'codebase_emissions': 0.05,
        'metadata': {'total_files': 10}
    }

def test_esg_exporter_initialization():
    exporter = ESGExporter()
    assert exporter.output_path.endswith('esg-report.pdf')

    exporter_custom = ESGExporter(output_path='/tmp/custom-report.pdf')
    assert exporter_custom.output_path == '/tmp/custom-report.pdf'

@patch('src.core.export.esg_exporter.SCICalculator')
def test_esg_export_success(mock_sci_calc, mock_results):
    # Setup mock SCICalculator
    mock_instance = MagicMock()
    mock_instance.get_sci_report.return_value = {
        'sci_score': 0.005,
        'unit': 'gCO2e/file',
        'energy_kwh': 0.1,
        'carbon_intensity': 0.5,
        'embodied_carbon': 0.0,
        'functional_unit': 'file'
    }
    mock_sci_calc.return_value = mock_instance

    # We patch weasyprint inside the module
    with patch('src.core.export.esg_exporter.Environment') as mock_env:
        # Mock jinja2 environment to avoid template parsing issues in mocked env
        mock_template = MagicMock()
        mock_template.render.return_value = "<html>Mock HTML</html>"

        mock_env_instance = MagicMock()
        mock_env_instance.get_template.return_value = mock_template
        mock_env.return_value = mock_env_instance

        # Patch the local weasyprint import inside export() method
        import builtins
        original_import = builtins.__import__

        mock_weasyprint = MagicMock()
        mock_html = MagicMock()
        mock_weasyprint.HTML.return_value = mock_html

        def side_effect(name, *args, **kwargs):
            if name == 'weasyprint':
                return mock_weasyprint
            return original_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=side_effect):
            exporter = ESGExporter(output_path='/tmp/test-esg-report.pdf')
            output_path = exporter.export(mock_results, project_name='TestProject')

            assert output_path == '/tmp/test-esg-report.pdf'
            mock_sci_calc.assert_called_once()
            mock_instance.get_sci_report.assert_called_once_with(mock_results)

            mock_weasyprint.HTML.assert_called_once_with(string="<html>Mock HTML</html>")
            mock_html.write_pdf.assert_called_once_with('/tmp/test-esg-report.pdf')

def test_esg_export_weasyprint_missing(mock_results):
    import builtins
    original_import = builtins.__import__

    def side_effect(name, *args, **kwargs):
        if name == 'weasyprint':
            raise ImportError("No module named 'weasyprint'")
        return original_import(name, *args, **kwargs)

    with patch('builtins.__import__', side_effect=side_effect):
        exporter = ESGExporter(output_path='/tmp/test-esg-report.pdf')
        output_path = exporter.export(mock_results, project_name='TestProject')

        # Should return empty string and log error
        assert output_path == ""
