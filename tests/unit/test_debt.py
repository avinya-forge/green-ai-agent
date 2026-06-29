import pytest
from src.core.domain import Project

def test_project_cleanliness_grade():
    project = Project(name="test", repo_url="http://test")

    project.total_remediation_time_minutes = 0
    assert project.get_cleanliness_grade() == "A"

    project.total_remediation_time_minutes = 30
    assert project.get_cleanliness_grade() == "B"

    project.total_remediation_time_minutes = 60
    assert project.get_cleanliness_grade() == "B"

    project.total_remediation_time_minutes = 120
    assert project.get_cleanliness_grade() == "C"

    project.total_remediation_time_minutes = 300
    assert project.get_cleanliness_grade() == "D"

    project.total_remediation_time_minutes = 500
    assert project.get_cleanliness_grade() == "F"

def test_project_remediation_effort_calculation():
    project = Project(name="test", repo_url="http://test")
    violations = [
        {"id": "rule_1", "line": 1, "severity": "high", "message": "msg", "effort": 60},
        {"id": "rule_2", "line": 2, "severity": "medium", "message": "msg", "effort": 15},
        {"id": "rule_3", "line": 3, "severity": "low", "message": "msg"} # Defaults to 0 effort if not present
    ]
    project.update_scan_results(violations, 0.0)
    assert project.total_remediation_time_minutes == 75
    assert project.get_cleanliness_grade() == "C"
