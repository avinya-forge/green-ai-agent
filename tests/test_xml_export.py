import pytest
import xml.etree.ElementTree as ET
from src.core.export.xml_exporter import JUnitXMLExporter

def test_xml_export(tmp_path):
    """Test JUnit XML export."""
    exporter = JUnitXMLExporter(str(tmp_path / "report.xml"))

    results = {
        'issues': [
            {
                'id': 'test_rule',
                'file': 'test.py',
                'line': 10,
                'message': 'Test failure',
                'severity': 'high'
            }
        ]
    }

    output_file = exporter.export(results, 'Test Project')

    assert output_file == str(tmp_path / "report.xml")

    tree = ET.parse(output_file)
    root = tree.getroot()

    assert root.tag == 'testsuites'
    testsuite = root.find('testsuite')
    assert testsuite.get('name') == 'Test Project'
    assert testsuite.get('tests') == '1'
    assert testsuite.get('failures') == '1'

    testcase = testsuite.find('testcase')
    assert testcase.get('classname') == 'test.py'
    assert testcase.get('name') == 'test_rule (Line 10)'

    failure = testcase.find('failure')
    assert failure.get('message') == 'Test failure'
    assert failure.get('type') == 'high'
