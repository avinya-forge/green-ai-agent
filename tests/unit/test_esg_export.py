"""
Tests for ESG export functionality.
"""
import sys
import pytest
from unittest.mock import MagicMock, patch
from src.core.export.esg_exporter import ESGExporter


class TestESGExporter:

    @pytest.fixture
    def sample_results(self):
        return {
            'issues': [
                {
                    'id': 'io_in_loop',
                    'file': 'src/main.py',
                    'line': 10,
                    'severity': 'critical',
                    'message': 'IO inside loop',
                    'effort': 'medium',
                    'energy_factor': '100x',
                    'tags': ['security']
                },
                {
                    'id': 'unused_variable',
                    'file': 'src/utils.py',
                    'line': 5,
                    'severity': 'low',
                    'message': 'Unused var',
                    'effort': 'trivial',
                    'energy_factor': '1x'
                },
                {
                    'id': 'hardcoded_secret',
                    'file': 'src/config.py',
                    'line': 20,
                    'severity': 'high',
                    'message': 'Hardcoded secret',
                    'effort': 'low',
                    'energy_factor': '1x',
                    'tags': ['security', 'secret']
                }
            ],
            'codebase_emissions': 0.005,
            'scanning_emissions': 0.001,
            'per_file_emissions': {
                'src/main.py': 0.004,
                'src/utils.py': 0.001
            }
        }

    @pytest.fixture
    def mock_sci_report(self):
        return {
            'sci_score': 0.005,
            'unit': 'gCO2eq',
            'energy_kwh': 0.001,
            'carbon_intensity': 400.0,
            'hardware_emissions': 0.0,
            'total_emissions': 0.005
        }

    def test_esg_export_success(self, sample_results, tmp_path, mock_sci_report):
        """Test ESG export logic with mocked WeasyPrint."""
        output_file = tmp_path / "esg-report.pdf"
        exporter = ESGExporter(str(output_file))

        # Create a mock WeasyPrint module
        mock_weasyprint = MagicMock()
        mock_html_class = MagicMock()
        mock_html_instance = MagicMock()
        mock_html_class.return_value = mock_html_instance
        mock_weasyprint.HTML = mock_html_class

        # Patch sys.modules and SCICalculator
        with patch.dict(sys.modules, {'weasyprint': mock_weasyprint}):
            with patch('src.core.export.esg_exporter.SCICalculator') as MockSCI:
                # Configure mock SCI calculator
                mock_sci_instance = MagicMock()
                mock_sci_instance.get_sci_report.return_value = mock_sci_report
                MockSCI.return_value = mock_sci_instance

                result_path = exporter.export(sample_results, "TestESGProject")

                assert result_path == str(output_file)

                # Verify HTML was instantiated
                mock_html_class.assert_called_once()
                call_args = mock_html_class.call_args

                if 'string' in call_args.kwargs:
                    html_content = call_args.kwargs['string']
                elif len(call_args.args) > 0:
                    html_content = call_args.args[0]
                else:
                    pytest.fail("HTML constructor called without string argument")

                # Check content for key ESG metrics
                assert "TestESGProject" in html_content
                assert "0.0050" in html_content  # SCI score
                assert "0.001000" in html_content  # Energy kWh
                assert "Critical Vulnerabilities: 1" in html_content
                assert "Secret Findings: 1" in html_content
                assert "SAST Violations: 2" in html_content
                assert "IN REVIEW" in html_content  # Compliance status due to 1 critical issue
                assert "1.5 hours" in html_content  # 3 issues * 0.5 hours

                # Verify write_pdf was called
                mock_html_instance.write_pdf.assert_called_once_with(str(output_file))

    def test_esg_export_import_error(self, sample_results, tmp_path):
        """Test behavior when WeasyPrint is missing."""
        output_file = tmp_path / "esg-report.pdf"
        exporter = ESGExporter(str(output_file))

        with patch.dict(sys.modules, {'weasyprint': None}):
            result_path = exporter.export(sample_results, "TestESGProject")
            assert result_path == ""
