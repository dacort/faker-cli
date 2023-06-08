from faker_cli.cli import main
from click.testing import CliRunner
import json


# Test that help is provided if the user provides no arguments
def test_default_help():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert result.output.startswith("Usage: main")
    assert "Options:" in result.output


# Write a test to make sure csv output works
def test_csv_output():
    runner = CliRunner()
    result = runner.invoke(main, ["pyint,user_name"])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert len(lines) == 2  # header is included
    assert lines[0] == "pyint,user_name"
    assert len(lines[1].split(",")) == 2


def test_json_output():
    runner = CliRunner()
    result = runner.invoke(main, ["pyint,user_name", "-f", "json"])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert len(lines) == 1
    data: dict = json.loads(lines[0])
    assert len(data.keys()) == 2
    assert list(data) == ["pyint", "user_name"]
    assert len(data.values()) == 2


def test_numlines():
    runner = CliRunner()
    for format in ["csv", "json"]:
        result = runner.invoke(main, ["pyint,user_name", "-f", format, "-n", "5"])
        assert result.exit_code == 0
        lines = result.output.strip().splitlines()
        assert len(lines) == (6 if format == "csv" else 5)

def test_custom_column_names():
    runner = CliRunner()
    result = runner.invoke(main, ["pyint,user_name", "-f", "json", "-c", "first,second"])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    data: dict = json.loads(lines[0])
    assert len(data.keys()) == 2
    assert list(data) == ["first", "second"]