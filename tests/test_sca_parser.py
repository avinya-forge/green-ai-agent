import pytest
from src.core.sca.manifest_parser import ManifestParser

def test_parse_requirements_txt():
    parser = ManifestParser()
    content = "fastapi==0.110.0\npydantic>=2.0.0\nrequests"
    deps = parser.parse_requirements_txt(content)

    assert len(deps) == 3
    assert deps[0]['name'] == 'fastapi'
    assert deps[0]['version'] == '0.110.0'
    assert deps[2]['name'] == 'requests'
    assert deps[2]['version'] == 'unknown'

def test_parse_package_json():
    parser = ManifestParser()
    content = '{"dependencies": {"react": "^18.2.0"}, "devDependencies": {"jest": "~29.0.0"}}'
    deps = parser.parse_package_json(content)

    assert len(deps) == 2
    names = [d['name'] for d in deps]
    assert 'react' in names
    assert 'jest' in names

    react_dep = next(d for d in deps if d['name'] == 'react')
    assert react_dep['version'] == '18.2.0'
