"""
Security Utilities for Green AI Agent.

Provides functions for input sanitization and validation to prevent common
security vulnerabilities like path traversal and command injection.
"""

import re
import os
from pathlib import Path
from typing import Optional, Union
import urllib.parse


def sanitize_path(
    path: Union[str, Path],
    allow_absolute: bool = False,
    restrict_to_base: Optional[Path] = None
) -> Path:
    """
    Sanitize a file path to prevent traversal attacks.

    Args:
        path: The input path string or Path object.
        allow_absolute: If True, allows absolute paths (still checked against
                        restrict_to_base if provided).
        restrict_to_base: If provided, ensures the resolved path is within
                          this directory.

    Returns:
        A resolved, absolute Path object.

    Raises:
        ValueError: If path is unsafe or violates restrictions.
    """
    if isinstance(path, str):
        path = Path(path)

    # Check for null bytes
    if '\0' in str(path):
        raise ValueError("Path contains null bytes")

    # Resolve path (expands symlinks and '..')
    try:
        # strict=False allows non-existent files (e.g. for output)
        resolved_path = path.resolve()
    except Exception:
        # Fallback if resolve fails (e.g. permission issues on parent)
        resolved_path = path.absolute()

    # If restrict_to_base is set, enforce it
    if restrict_to_base:
        base = restrict_to_base.resolve()
        try:
            resolved_path.relative_to(base)
        except ValueError:
            raise ValueError(
                f"Path traversal attempt: {path} is outside base "
                f"directory {base}"
            )
    # If restrict_to_base is NOT set, and not allowing absolute paths
    # (user input must be relative to CWD)
    elif not allow_absolute:
        cwd = Path.cwd().resolve()
        try:
            resolved_path.relative_to(cwd)
        except ValueError:
            raise ValueError(
                f"Path traversal attempt: {path} is outside "
                "current working directory"
            )

    return resolved_path


def sanitize_project_name(name: str) -> str:
    """
    Sanitize project name to be safe for filenames and display.
    Allows alphanumeric, hyphens, underscores, spaces.
    """
    if not name:
        return "Unnamed Project"

    # Remove potentially dangerous chars
    # Allow a-z, A-Z, 0-9, -, _, space
    sanitized = re.sub(r'[^a-zA-Z0-9\-\_\s]', '', name)

    # Trim spaces
    sanitized = sanitized.strip()

    if not sanitized:
        return "Unnamed Project"

    return sanitized[:255]  # Limit length


def is_safe_git_url(url: str) -> bool:
    """
    Check if a git URL is safe.
    Allows http, https, ssh (git@).
    Rejects file://, local paths, and command injection characters.
    """
    if not url:
        return False

    # Check for command injection chars (basic)
    if any(c in url for c in [';', '&', '|', '`', '$', '\n', '\r']):
        return False

    # Check for file:// scheme explicitly
    if url.startswith('file://'):
        return False

    # Parse URL
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False

    # Check scheme
    if parsed.scheme in ['http', 'https', 'ssh']:
        return True

    # Handle git@github.com:user/repo (scp-like syntax)
    # urlparse might not handle it well if no scheme
    if url.startswith('git@'):
        # regex for git@host:path
        # Allow alphanumeric, dots, hyphens, underscores in host (e.g. internal network)
        # Allow alphanumeric, slashes, dots, hyphens, underscores in path (e.g. repo names)
        if re.match(r'^git@[a-zA-Z0-9\.\-\_]+:[a-zA-Z0-9\/\.\-\_]+$', url):
            return True

    return False
