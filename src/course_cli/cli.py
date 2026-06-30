import click
import yaml
from pathlib import Path
from .validate import validate_course

@click.group()
def main():
    """Course CLI - инструмент для структурирования учебных курсов."""
    pass

@click.command()
@click.argument('title', required=False)
def init(title):
    """Инициализировать шаблон нового курса."""
    # Если название не передали
    if not title:
        title = click.prompt("Введите название курса")

    # Создаем структуру папок
    course_path = Path(title)
    if course_path.exists():
        click.secho(f"Ошибка: Папка {title} уже существует!", fg="red")
        return

    # Создаем дерево директорий
    (course_path / "modules").mkdir(parents=True)
    (course_path / "lessons").mkdir(parents=True)

    # Создаем базовые файлы шаблона
    (course_path / "index.md").write_text(f"# {title}\n\nWelcome!")
    (course_path / "lessons/lesson_1.md").write_text(f"# Урок 1\n\n First lesson")

    # Создаем файл course.yaml
    config_data = {
        "title": title,
        "outcomes": [],
        "skills": []
    }
    with open(course_path / "course.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config_data, f, allow_unicode=True)

    click.secho(f"Успех! Курс '{title}' создан.", fg="green")


@click.command()
@click.argument('course_path', type=click.Path(exists=True))
def validate(course_path):
    """Проверить курс на наличие ошибок и метаданных."""
    path = Path(course_path)
    errors = validate_course(path)
    
    if errors:
        for error in errors:
            click.secho(f"Ошибка: {error}", fg="red")
        exit(1)
    else:
        click.secho("Курс провалидирован успешно!", fg="green")

@click.command()
def report():
    """Сгенерировать отчет и отправить xAPI-событие."""
    click.echo("Команда report в разработке...")

main.add_command(init)
main.add_command(validate)
main.add_command(report)