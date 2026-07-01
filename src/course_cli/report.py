import yaml
from pathlib import Path

def get_course_stats(course_path: Path) -> dict:
    """Сбор статистики по курсу: количество уроков и учебных результатов."""
    stats = {"outcomes_count": 0, "lessons_count": 0, "title": "Unknown"}
    
    course_yaml = course_path / "course.yaml"
    if course_yaml.exists():
        with open(course_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            stats["title"] = data.get("title", "Unknown")
            stats["outcomes_count"] = len(data.get("outcomes") or [])
            
    modules_dir = course_path / "modules"
    if modules_dir.exists():
        # rglob ("recursive glob") ищет файлы во всех вложенных папках модулей
        stats["lessons_count"] = len(list(modules_dir.rglob("*.md")))
                
    return stats