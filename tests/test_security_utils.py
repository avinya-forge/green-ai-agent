"""
Tests for security utilities.
"""

import pytest
from pathlib import Path
from src.utils.security import sanitize_path, sanitize_project_name, is_safe_git_url

class TestSanitizePath:
    def test_sanitize_path_relative(self, tmp_path):
        """Test relative path sanitization."""
        # Using pytest's tmp_path fixture which creates a temp directory
        # This will be treated as CWD if we change to it, but we're not changing CWD.
        # sanitize_path defaults to checking against Path.cwd().
        # So we need to ensure we pass a path relative to actual CWD or mock CWD.

        # We can't easily mock Path.cwd() without patching.
        # So we'll use a relative path that is safe (e.g., 'foo.txt')
        path = sanitize_path('foo.txt')
        assert path.name == 'foo.txt'
        assert path.is_absolute()
        assert str(path).startswith(str(Path.cwd()))

    def test_sanitize_path_traversal(self):
        """Test path traversal detection."""
        with pytest.raises(ValueError, match="outside current working directory"):
            sanitize_path('../foo.txt')

        with pytest.raises(ValueError, match="outside current working directory"):
            sanitize_path('/etc/passwd')

    def test_sanitize_path_allow_absolute(self):
        """Test absolute path allowance."""
        # sanitize_path(allow_absolute=True) allows absolute paths IF restrict_to_base is not set.
        # However, sanitize_path logic is:
        # if not allow_absolute: check cwd.
        # So if allow_absolute=True, it skips CWD check.

        # Test absolute path (use a safe one like /tmp/foo.txt)
        # Note: on Windows this might fail if drive letters differ.
        # Using a path relative to root.
        path_str = str(Path.cwd().parent / 'foo.txt')
        path = sanitize_path(path_str, allow_absolute=True)
        assert str(path) == path_str

    def test_sanitize_path_restrict_to_base(self, tmp_path):
        """Test restrict_to_base functionality."""
        base = tmp_path
        safe_path = base / 'subdir' / 'file.txt'
        unsafe_path = base.parent / 'file.txt'

        # Create subdir
        (base / 'subdir').mkdir()

        # Safe path
        sanitized = sanitize_path(safe_path, restrict_to_base=base)
        assert sanitized == safe_path.resolve()

        # Unsafe path
        with pytest.raises(ValueError, match=f"outside base directory {base.resolve()}"):
            sanitize_path(unsafe_path, restrict_to_base=base)

    def test_sanitize_path_null_bytes(self):
        """Test null byte rejection."""
        with pytest.raises(ValueError, match="Path contains null bytes"):
            sanitize_path('foo\0.txt')


class TestSanitizeProjectName:
    def test_sanitize_project_name_valid(self):
        assert sanitize_project_name("My Project") == "My Project"
        assert sanitize_project_name("project-123_v2") == "project-123_v2"

    def test_sanitize_project_name_invalid(self):
        assert sanitize_project_name("My$Project!") == "MyProject"
        assert sanitize_project_name("../Hack") == "Hack"
        assert sanitize_project_name("  trimmed  ") == "trimmed"

    def test_sanitize_project_name_empty(self):
        assert sanitize_project_name("") == "Unnamed Project"
        assert sanitize_project_name("   ") == "Unnamed Project"


class TestIsSafeGitUrl:
    def test_is_safe_git_url_valid(self):
        assert is_safe_git_url("https://github.com/user/repo.git")
        assert is_safe_git_url("http://github.com/user/repo.git")
        assert is_safe_git_url("ssh://git@github.com/user/repo.git")
        assert is_safe_git_url("git@github.com:user/repo.git")
        assert is_safe_git_url("git@gitlab.com:group/project.git")
        assert is_safe_git_url("git@my_host:my_user/my_repo.git")
        assert is_safe_git_url("git@internal.server.com:project/repo_with_underscores.git")

    def test_is_safe_git_url_invalid(self):
        assert not is_safe_git_url("file:///etc/passwd")
        assert not is_safe_git_url("/etc/passwd")
        assert not is_safe_git_url("ftp://example.com/repo.git")
        assert not is_safe_git_url("http://example.com/repo.git; rm -rf /")
        assert not is_safe_git_url("git@github.com:user/repo.git; echo pwned")
        assert not is_safe_git_url("")
