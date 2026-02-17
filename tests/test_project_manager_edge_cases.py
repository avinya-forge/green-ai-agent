"""
Edge case tests for ProjectManager
"""

import pytest
from unittest.mock import patch, MagicMock
from src.core.project_manager import ProjectManager, ProjectException
from src.core.domain import Project

@pytest.fixture
def mock_project_manager():
    # Use patch to avoid file system operations in init
    with patch('src.core.project_manager.Path.mkdir'), \
         patch('src.core.project_manager.ProjectManager._load_projects'):
        pm = ProjectManager()
        pm.projects = {}
        pm.projects_by_name = {}
        yield pm

def test_add_project_none_branch(mock_project_manager):
    """Test adding a project with None as branch defaults to main."""
    with patch('src.core.project_manager.ProjectManager._save_projects'):
        project = mock_project_manager.add_project(
            name="Test",
            repo_url="http://example.com",
            branch=None
        )
        assert project.branch == "main"

def test_add_project_duplicate(mock_project_manager):
    """Test adding a duplicate project raises exception."""
    with patch('src.core.project_manager.ProjectManager._save_projects'):
        mock_project_manager.add_project("Test", "url")

        with pytest.raises(ProjectException):
            mock_project_manager.add_project("Test", "url2")

def test_remove_project_not_found(mock_project_manager):
    """Test removing a non-existent project raises exception."""
    with pytest.raises(ProjectException):
        mock_project_manager.remove_project("NonExistent")

def test_remove_system_project(mock_project_manager):
    """Test removing a system project raises exception."""
    with patch('src.core.project_manager.ProjectManager._save_projects'):
        project = mock_project_manager.add_project("System", "url", is_system=True)

        with pytest.raises(ProjectException) as exc:
            mock_project_manager.remove_project("System")
        assert "Cannot delete system project" in str(exc.value)

def test_get_project_by_id_or_name(mock_project_manager):
    """Test retrieving project by ID or Name."""
    with patch('src.core.project_manager.ProjectManager._save_projects'):
        project = mock_project_manager.add_project("Test", "url")

        # By Name
        assert mock_project_manager.get_project("Test") == project
        # By ID
        assert mock_project_manager.get_project(project.id) == project
        # Not found
        assert mock_project_manager.get_project("Other") is None

def test_list_projects_sorting(mock_project_manager):
    """Test sorting of projects list."""
    with patch('src.core.project_manager.ProjectManager._save_projects'):
        p1 = mock_project_manager.add_project("B", "url")
        p2 = mock_project_manager.add_project("A", "url")

        # Sort by name
        projects = mock_project_manager.list_projects(sort_by="name")
        assert projects[0].name == "A"
        assert projects[1].name == "B"

def test_update_scan_results(mock_project_manager):
    """Test updating scan results."""
    with patch('src.core.project_manager.ProjectManager._save_projects'):
        mock_project_manager.add_project("Test", "url")

        mock_project_manager.update_project_scan(
            "Test",
            violations=10,
            emissions=5.0
        )

        project = mock_project_manager.get_project("Test")
        assert project.latest_violations == 10
        assert project.total_emissions == 5.0
