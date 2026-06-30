from click.testing import CliRunner
from src.course_cli.cli import main

def test_cli_help():
    """Проверяем, что справка `--help` выводится без ошибок."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage: main" in result.output

def test_init_command():
    """Проверяем, что команда init вызывается и выводит текст-заглушку."""
    runner = CliRunner()
    result = runner.invoke(main, ["init"])
    assert result.exit_code == 0
    assert "Команда init в разработке..." in result.output