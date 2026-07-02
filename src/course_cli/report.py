import yaml
from pathlib import Path

def get_course_stats(course_path: Path) -> dict:
    """Расширенный сбор статистики по курсу."""
    stats = {
        "title": "Unknown",
        "outcomes": [],
        "skills": [],
        "modules_count": 0,
        "lessons_count": 0,
        "empty_modules": 0
    }
    
    course_yaml = course_path / "course.yaml"
    if course_yaml.exists():
        with open(course_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            stats["title"] = data.get("title", "Unknown")
            stats["outcomes"] = data.get("outcomes") or []
            stats["skills"] = data.get("skills") or []
            
    modules_dir = course_path / "modules"
    if modules_dir.exists():
        # Считаем только папки модулей
        modules = [d for d in modules_dir.iterdir() if d.is_dir() and d.name.startswith("module_")]
        stats["modules_count"] = len(modules)
        
        # Считаем уроки и ищем пустые модули
        for mod in modules:
            lessons = list(mod.glob("*.md"))
            stats["lessons_count"] += len(lessons)
            if len(lessons) == 0:
                stats["empty_modules"] += 1
                
    return stats