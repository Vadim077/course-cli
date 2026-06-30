import os
import shutil
from click.testing import CliRunner
from src.course_cli.cli import main

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
        result = runner.invoke(main, ["init", "MyTestCourse"])
        
        assert result.exit_code == 0
        assert os.path.exists("MyTestCourse")
        assert os.path.exists("MyTestCourse/course.yaml")
        assert os.path.exists("MyTestCourse/modules")
        assert os.path.exists("MyTestCourse/lessons/lesson_1.md")