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
    if not title:
        title = click.prompt("Введите название курса")
        
    modules_count = click.prompt("Введите количество модулей", type=int, default=1)
    lessons_count = click.prompt("Введите количество уроков в каждом модуле", type=int, default=1)
    
    # Новые вопросы для сбора метаданных (ТЗ п.6)
    outcomes_input = click.prompt("Введите учебные результаты (через запятую) или оставьте пустым", default="", show_default=False)
    skills_input = click.prompt("Введите связанные навыки (через запятую) или оставьте пустым", default="", show_default=False)

    # Превращаем строки в списки, удаляя лишние пробелы
    outcomes = [x.strip() for x in outcomes_input.split(",")] if outcomes_input else []
    skills = [x.strip() for x in skills_input.split(",")] if skills_input else []

    course_path = Path(title)
    if course_path.exists():
        click.secho(f"Ошибка: Папка {title} уже существует!", fg="red")
        return

    course_path.mkdir(parents=True)
    (course_path / "index.md").write_text(f"# {title}\n\nДобро пожаловать на курс!", encoding="utf-8")

    modules_dir = course_path / "modules"
    modules_dir.mkdir()

    for m in range(1, modules_count + 1):
        mod_path = modules_dir / f"module_{m}"
        mod_path.mkdir()
        for l in range(1, lessons_count + 1):
            lesson_file = mod_path / f"lesson_{l}.md"
            # Для теста добавим "правильную" и "битую" ссылку в первый урок
            content = f"# Модуль {m} - Урок {l}\n\nТекст урока.\n"
            if m == 1 and l == 1:
                content += "\n[Ссылка на индекс](../../index.md)\n[Битая ссылка](missing.md)"
            lesson_file.write_text(content, encoding="utf-8")

    # Сохраняем новые данные в YAML
    config_data = {
        "title": title,
        "outcomes": outcomes,
        "skills": skills
    }
    with open(course_path / "course.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config_data, f, allow_unicode=True)

    total_lessons = modules_count * lessons_count
    click.secho(f"Успех! Курс '{title}' создан (Модулей: {modules_count}, Уроков: {total_lessons}).", fg="green")



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