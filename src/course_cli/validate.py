import yaml
import click
from pathlib import Path

def validate_course(course_path: Path):
    """Основная функция валидации курса."""
    errors = []
    course_yaml = course_path / "course.yaml"
    
    if not course_yaml.exists():
        errors.append(f"Файл {course_yaml} не найден!")
        return errors

    with open(course_yaml, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not data.get("title"):
        errors.append("Отсутствует название курса (title).")
    if not data.get("outcomes"):
        errors.append("Список результатов обучения (outcomes) пуст.")

    lesson_path = course_path / "modules" / "module_1" / "lesson_1.md"
    if not lesson_path.exists():
        errors.append(f"Битая ссылка: файл {lesson_path} не существует.")

    return errors