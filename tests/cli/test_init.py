"""
Tests for init command.
"""
from click.testing import CliRunner
from src.cli.commands.init import init
import os
import yaml

def test_init_command(tmp_path):
    runner = CliRunner()

    # Run in a temporary directory
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(init)

        assert result.exit_code == 0
        assert "Initialized configuration at .green-ai.yaml" in result.output

        # Verify file content
        assert os.path.exists(".green-ai.yaml")
        with open(".green-ai.yaml") as f:
            content = yaml.safe_load(f)
            assert "languages" in content
            assert "rules" in content

def test_init_command_overwrite(tmp_path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create dummy file
        with open(".green-ai.yaml", "w") as f:
            f.write("dummy: true")

        # Run init, should prompt
        result = runner.invoke(init, input="y\n")

        assert result.exit_code == 0
        assert "Configuration file already exists" in result.output

        # Verify it was overwritten
        with open(".green-ai.yaml") as f:
            content = yaml.safe_load(f)
            assert "languages" in content

def test_init_command_no_overwrite(tmp_path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create dummy file
        with open(".green-ai.yaml", "w") as f:
            f.write("dummy: true")

        # Run init, say no
        result = runner.invoke(init, input="n\n")

        assert result.exit_code == 0

        # Verify it was NOT overwritten
        with open(".green-ai.yaml") as f:
            content = yaml.safe_load(f)
            assert "dummy" in content
