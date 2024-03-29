import json

import deltalake
from click.testing import CliRunner

from faker_cli.cli import main


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


def test_deltalake_output(tmp_path):
    runner = CliRunner()
    file = tmp_path / "table"
    result = runner.invoke(main, ["pyint,user_name", "-f", "deltalake", "-o", file])
    assert result.exit_code == 0
    delta_table = deltalake.DeltaTable(file)
    arrow_table = delta_table.to_pyarrow_table()
    lines_count = arrow_table.num_rows
    assert lines_count == 1

    column_names = arrow_table.column_names
    assert column_names == ["pyint", "user_name"]
    assert arrow_table.num_columns == 2


def test_provider_args():
    runner = CliRunner()
    result = runner.invoke(main, ["-n", "10", "pyint(1;10)", "-f", "json", "-c", "id"])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    for line in lines:
        data: dict = json.loads(line)
        assert data["id"] in range(1, 11)


def test_unique_provider_args():
    runner = CliRunner()
    result = runner.invoke(main, ["-n", "10", "unique.pyint(1;10)", "-f", "json", "-c", "id"])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    vals = []
    for line in lines:
        data: dict = json.loads(line)
        assert data["id"] in range(1, 11)
        vals.append(data["id"])

    assert set(vals) == set(range(1, 11))


def test_unique_provider_args_limit():
    runner = CliRunner()
    result = runner.invoke(main, ["-n", "10", "unique.pyint(1;5)", "-f", "json", "-c", "id"])
    assert result.exit_code == 1
