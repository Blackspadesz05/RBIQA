from typer.testing import CliRunner

from rbiqa import __version__
from rbiqa.cli import app

runner = CliRunner()


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_show_config_outputs_json() -> None:
    result = runner.invoke(app, ["show-config"])
    assert result.exit_code == 0
    assert '"project_name": "rbiqa"' in result.output