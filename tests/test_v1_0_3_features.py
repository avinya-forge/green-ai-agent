import os
import json
import pytest
from click.testing import CliRunner
from src.cli.main import cli
from pathlib import Path

def test_baseline_cli_flow(tmp_path):
    runner = CliRunner()
    test_file = tmp_path / "vuln.py"
    test_file.write_text("print('test')")

    os.chdir(tmp_path)

    # 1. Create baseline
    result = runner.invoke(cli, ['baseline', 'create', '.', '--language', 'python'])
    assert result.exit_code == 0
    assert os.path.exists(".green-ai/baseline.json")

    # 2. Scan should now show 0 new issues
    result = runner.invoke(cli, ['scan', '.', '--language', 'python'])
    assert "Found 0 issues" in result.output
    assert "Baseline Delta" in result.output

def test_sbom_cli_flow(tmp_path):
    runner = CliRunner()
    os.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("pydantic==2.12.5")

    # 1. Generate CycloneDX
    result = runner.invoke(cli, ['sbom', '.', '--format', 'cyclonedx'])
    assert result.exit_code == 0

    # 2. Generate ESG Report
    result = runner.invoke(cli, ['sbom', '.', '--esg-report'])
    assert result.exit_code == 0
    assert "ESG Report generated" in result.output

def test_inline_suppression_cli(tmp_path):
    runner = CliRunner()
    test_file = tmp_path / "suppress.py"
    # Note: no leading newline to ensure line numbers match
    test_file.write_text("# green-ai: ignore next-line excessive_logging\nprint('test')")
    os.chdir(tmp_path)
    result = runner.invoke(cli, ['scan', 'suppress.py', '--language', 'python'])
    assert "Found 0 issues" in result.output

def test_external_suppression_cli(tmp_path):
    runner = CliRunner()
    test_file = tmp_path / "ext_suppress.py"
    test_file.write_text("print('test')")

    os.chdir(tmp_path)
    os.makedirs(".green-ai", exist_ok=True)
    with open(".green-ai/suppress.yaml", "w") as f:
        f.write("suppressions:\n  - rule_id: excessive_logging\n    file: ext_suppress.py\n    reason: 'Testing'\n")

    result = runner.invoke(cli, ['scan', 'ext_suppress.py', '--language', 'python'])
    assert "Found 0 issues" in result.output
