import click
import yaml
from pathlib import Path
from .validate import validate_course
from .report import get_course_stats
from .xapi import log_event 

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
    
    outcomes_input = click.prompt("Введите учебные результаты (через запятую) или оставьте пустым", default="", show_default=False)
    skills_input = click.prompt("Введите связанные навыки (через запятую) или оставьте пустым", default="", show_default=False)

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
            content = f"# Модуль {m} - Урок {l}\n\nТекст урока.\n"
            if m == 1 and l == 1:
                content += "\n[Ссылка на индекс](../../index.md)\n[Битая ссылка](missing.md)"
            lesson_file.write_text(content, encoding="utf-8")

    config_data = {
        "title": title,
        "outcomes": outcomes,
        "skills": skills
    }
    with open(course_path / "course.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config_data, f, allow_unicode=True)

    total_lessons = modules_count * lessons_count
    click.secho(f"Успех! Курс '{title}' создан (Модулей: {modules_count}, Уроков: {total_lessons}).", fg="green")
    
    log_event(
        course_path=course_path,
        verb="initialized",
        object_id=title,
        context_info=f"Модулей: {modules_count}, Уроков: {total_lessons}"
    )


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
        log_event(
            course_path=path,
            verb="validated",
            object_id=path.name,
            context_info="Успешная валидация структуры и ссылок"
        )


@click.command()
@click.argument('course_path', type=click.Path(exists=True))
def report(course_path):
    """Сгенерировать отчет и сохранить xAPI-событие."""
    path = Path(course_path)
    stats = get_course_stats(path)

    click.secho(f"\n--- Отчет по курсу: {stats['title']} ---", fg="cyan")
    click.echo(f"Учебных результатов: {stats['outcomes_count']}")
    click.echo(f"Количество уроков: {stats['lessons_count']}")
    click.echo("-----------------------------------\n")

    if click.confirm('Сформировать отчет xAPI и сохранить локально?'):
        log_event(
            course_path=path,
            verb="reported",
            object_id=stats['title'],
            context_info=f"Статистика: {stats['lessons_count']} уроков, {stats['outcomes_count']} результатов."
        )
        click.secho(f"xAPI событие успешно сохранено в {path / 'log.json'}", fg="green")
    else:
        click.secho("Отправка xAPI отменена.", fg="yellow")

main.add_command(init)
main.add_command(validate)
main.add_command(report)