import click
import yaml
from pathlib import Path
from .validate import validate_course
import json
from datetime import datetime, timezone
from .report import get_course_stats

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
@click.argument('course_path', type=click.Path(exists=True))
def report(course_path):
    """Сгенерировать отчет и сохранить xAPI-событие."""
    path = Path(course_path)
    stats = get_course_stats(path)

    # Вывод статистики
    click.secho(f"\n--- Отчет по курсу: {stats['title']} ---", fg="cyan")
    click.echo(f"Учебных результатов: {stats['outcomes_count']}")
    click.echo(f"Количество уроков: {stats['lessons_count']}")
    click.echo("-----------------------------------\n")

    # Интерактивный запрос
    if click.confirm('Сформировать отчет xAPI и сохранить локально?'):
        xapi_event = {
            "actor": "teacher",
            "verb": "course_reported",
            "object": stats['title'],
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

        # Сохраняем в файл log.json
        log_dir = Path("data/examples")
        log_dir.mkdir(parents=True, exist_ok=True) # Создаем папку, если вдруг ее нет
        log_file = log_dir / "log.json"

        # Читаем старые логи, чтобы не перезаписывать их, а добавлять
        logs = []
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    pass

        logs.append(xapi_event)

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

        click.secho(f"xAPI событие успешно сохранено в {log_file}", fg="green")
    else:
        click.secho("Отправка xAPI отменена.", fg="yellow")

main.add_command(init)
main.add_command(validate)
main.add_command(report)