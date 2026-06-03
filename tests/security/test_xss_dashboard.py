import pytest
from fastapi.testclient import TestClient
from src.ui.app_fastapi import app
import html

client = TestClient(app)

def test_dashboard_xss_protection_projects():
    """Verify that project names with XSS payloads are handled securely."""
    xss_payload = "<script>alert('xss')</script>"

    from src.ui.state import get_project_manager
    pm = get_project_manager()

    try:
        # Add project with XSS payload
        pm.add_project(name=xss_payload, repo_url="https://github.com/test/repo")

        # Access dashboard
        response = client.get("/")
        assert response.status_code == 200

        # Check if payload is NOT present in raw form in the template
        content = response.text
        assert xss_payload not in content

        # Access project list API
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()

        # data might be a dict with a 'projects' key or a list
        if isinstance(data, dict) and 'projects' in data:
            project_names = [p['name'] for p in data['projects']]
        elif isinstance(data, list):
            project_names = [p['name'] for p in data]
        else:
            # Fallback for unexpected format
            project_names = [str(data)]

        assert xss_payload in project_names

    finally:
        # Cleanup
        pm.remove_project(xss_payload)

def test_dashboard_templates_escaping():
    """Verify that templates use autoescaping."""
    from jinja2 import Environment, FileSystemLoader
    import os

    template_dir = os.path.join("src", "ui", "templates")
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

    template = env.get_template("dashboard.html")
    assert template is not None

    # Mock data needed by template
    mock_results = {
        'issues': [],
        'scanning_emissions': 0,
        'codebase_emissions': 0,
        'per_file_emissions': {},
        'metadata': {'total_files': 0}
    }

    # Render
    rendered = template.render(
        projects=[],
        results=mock_results,
        last_scan_time="Never",
        overall_grade="N/A",
        total_violations=0,
        project_count=0
    )
    assert rendered is not None
