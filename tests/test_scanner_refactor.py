from src.core.scanner import Scanner
from src.core.scanner.discovery import FileDiscoverer


def test_scanner_imports():
    """Verify that Scanner can be imported from the new package."""
    assert Scanner is not None


def test_file_discoverer(tmp_path):
    """Verify FileDiscoverer logic."""
    # Setup dummy files
    d = tmp_path / "subdir"
    d.mkdir()
    p1 = d / "hello.py"
    p1.write_text("print('hello')")
    p2 = d / "ignore.me"
    p2.write_text("ignore")

    # Mock config loader
    class MockConfigLoader:
        def get_ignored_files(self):
            return ['*.me']

    discoverer = FileDiscoverer(MockConfigLoader())
    files = discoverer.get_files(str(d))

    assert len(files) == 1
    assert str(p1) in files[0]
    assert "ignore.me" not in files[0]


def test_scanner_init():
    """Verify Scanner initialization."""
    scanner = Scanner(language='python')
    assert scanner.language == 'python'
    assert scanner.rule_repo is not None
    assert scanner.remediation_engine is not None
