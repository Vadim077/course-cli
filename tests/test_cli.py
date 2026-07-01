import os
import shutil
from click.testing import CliRunner
from course_cli.cli import main

def test_cli_help():
    """Проверяем, что справка `--help` выводится без ошибок."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage: main" in result.output

def test_init_creates_files(tmp_path):
    """Проверяем, что команда init создает папки и файлы."""
    # Создаем временную директорию для теста
    runner = CliRunner()
    # Запускаем init внутри временной директории
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["init", "MyTestCourse"], input="2\n3\n")
        
        assert result.exit_code == 0
        assert os.path.exists("MyTestCourse/course.yaml")
        assert os.path.exists("MyTestCourse/modules/module_1/lesson_1.md")
        assert os.path.exists("MyTestCourse/modules/module_2/lesson_3.md")

def test_validate_command_failure(tmp_path):
    """Проверяем, что validate ругается на пустой конфиг."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(main, ["init", "BadCourse"], input="\n\n")        
        # Портим конфиг
        with open("BadCourse/course.yaml", "w", encoding="utf-8") as f:
            f.write("title: ''\noutcomes: []\n")
        
        result = runner.invoke(main, ["validate", "BadCourse"])
        assert result.exit_code != 0
        assert "Ошибка" in result.output


def test_report_command(tmp_path):
    """Проверяем генерацию отчета и сохранение лога."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(main, ["init", "ReportCourse"], input="\n\n")
        result = runner.invoke(main, ["report", "ReportCourse"], input="y\n")
        
        assert result.exit_code == 0
        assert "Отчет по курсу: ReportCourse" in result.output
        assert "xAPI событие успешно сохранено" in result.output
        assert os.path.exists("data/examples/log.json")