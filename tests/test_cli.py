import os
import yaml
from pathlib import Path
from click.testing import CliRunner
from course_cli.cli import main

def test_init_creates_files(tmp_path):
    """Проверяем генерацию модулей, уроков и сбор метаданных."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Имитируем ввод пользователя для создания курса
        result = runner.invoke(main, ["init", "MyTestCourse"], input="2\n3\nЗнать Python\nGit, Docker\n")
        
        assert result.exit_code == 0
        assert os.path.exists("MyTestCourse/course.yaml")
        assert os.path.exists("MyTestCourse/modules/module_1/lesson_1.md")
        
        with open("MyTestCourse/course.yaml", "r", encoding="utf-8") as f:
            content = f.read()
            assert "Знать Python" in content
            assert "Docker" in content


def test_validate_success(tmp_path):
    """Проверяем, что идеальный курс успешно проходит валидацию."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(main, ["init", "GoodCourse"], input="2\n2\nРезультат 1\nНавык 1\n")
        
        # Перезаписываем первый урок, чтобы убрать дефолтную битую ссылку, 
        # которую команда init создает для демонстрации
        Path("GoodCourse/modules/module_1/lesson_1.md").write_text("# Урок 1\n\nЧистый контент.", encoding="utf-8")
        
        result = runner.invoke(main, ["validate", "GoodCourse"])
        assert result.exit_code == 0
        assert "Курс провалидирован успешно" in result.output


def test_validate_missing_outcomes(tmp_path):
    """Проверяем, что validate выдает ошибку, если список outcomes пуст."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Передаем пустую строку на вопрос об outcomes
        runner.invoke(main, ["init", "NoOutcomesCourse"], input="1\n1\n\nНавык 1\n")
        
        result = runner.invoke(main, ["validate", "NoOutcomesCourse"])
        assert result.exit_code != 0
        assert "Список результатов обучения (outcomes) пуст" in result.output


def test_validate_missing_skills_warning(tmp_path):
    """Проверяем, что отсутствие skills — это предупреждение, но не критическая ошибка."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Передаем пустую строку на вопрос о skills
        runner.invoke(main, ["init", "NoSkillsCourse"], input="1\n1\nРезультат 1\n\n")
        Path("NoSkillsCourse/modules/module_1/lesson_1.md").write_text("# Урок 1", encoding="utf-8")
        
        result = runner.invoke(main, ["validate", "NoSkillsCourse"])
        # Так как это warning, программа должна успешно завершиться (exit_code 0)
        assert result.exit_code == 0
        assert "Список навыков (skills) пуст. Рекомендуется заполнить" in result.output


def test_validate_missing_module_sequence(tmp_path):
    """Проверяем обнаружение пропущенного модуля в структуре папок."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(main, ["init", "MissingModCourse"], input="3\n1\nРезультат 1\nНавык 1\n")
        Path("MissingModCourse/modules/module_1/lesson_1.md").write_text("# Урок 1", encoding="utf-8")
        
        # Физически удаляем module_2, чтобы сломать последовательность папок
        mod2_path = Path("MissingModCourse/modules/module_2")
        for f in mod2_path.iterdir():
            f.unlink()
        mod2_path.rmdir()
        
        result = runner.invoke(main, ["validate", "MissingModCourse"])
        assert result.exit_code != 0
        assert "Пропущен модуль 'module_2'" in result.output


def test_validate_missing_lesson_sequence(tmp_path):
    """Проверяем обнаружение пропущенного урока внутри модуля."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(main, ["init", "MissingLesCourse"], input="1\n3\nРезультат 1\nНавык 1\n")
        Path("MissingLesCourse/modules/module_1/lesson_1.md").write_text("# Урок 1", encoding="utf-8")
        
        # Удаляем второй урок из трех сгенерированных
        Path("MissingLesCourse/modules/module_1/lesson_2.md").unlink()
        
        result = runner.invoke(main, ["validate", "MissingLesCourse"])
        assert result.exit_code != 0
        assert "В module_1 пропущен урок 'lesson_2.md'" in result.output


def test_validate_broken_links(tmp_path):
    """Проверяем, что валидатор находит битые markdown-ссылки."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(main, ["init", "BrokenLinkCourse"], input="1\n1\nРезультат 1\nНавык 1\n")
        # Команда init автоматически создает ссылку на missing.md. Оставляем её.
        
        result = runner.invoke(main, ["validate", "BrokenLinkCourse"])
        assert result.exit_code != 0
        assert "Битая ссылка в modules" in result.output
        assert "missing.md" in result.output


def test_report_command(tmp_path):
    """Проверяем работоспособность команды генерации отчета."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(main, ["init", "ReportCourse"], input="\n\n\n\n")
        result = runner.invoke(main, ["report", "ReportCourse"], input="y\n")
        
    assert result.exit_code == 0
    assert "ReportCourse" in result.output
    assert "Модулей:" in result.output
    assert "xAPI событие успешно сохранено" in result.output