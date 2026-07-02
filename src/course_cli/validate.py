import click
import yaml
from pathlib import Path
import re

def validate_course(course_dir):
    """Проверить структуру и метаданные курса."""
    course_path = Path(course_dir)
    config_path = course_path / "course.yaml"
    errors = []

    click.secho(f"🔍 Запуск проверки курса '{course_dir}'...", fg="cyan")

    # 1. Проверка YAML
    if not config_path.exists():
        return ["Файл course.yaml не найден."]

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not data.get("outcomes"):
        errors.append("Список результатов обучения (outcomes) пуст.")

    if not data.get("skills"):
        click.secho("Внимание: Список навыков (skills) пуст. Рекомендуется заполнить.", fg="yellow")

    # 2. Проверка последовательности модулей и уроков
    modules_dir = course_path / "modules"
    if modules_dir.exists():
        module_dirs = [d for d in modules_dir.iterdir() if d.is_dir() and d.name.startswith("module_")]
        module_nums = []
        for d in module_dirs:
            try:
                module_nums.append(int(d.name.split("_")[1]))
            except (ValueError, IndexError):
                pass

        if module_nums:
            max_mod = max(module_nums)
            for i in range(1, max_mod + 1):
                if i not in module_nums:
                    errors.append(f"Пропущен модуль 'module_{i}'")

        # Проверяем уроки внутри каждого модуля
        for m_dir in module_dirs:
            lesson_files = list(m_dir.glob("lesson_*.md"))
            lesson_nums = []
            for f in lesson_files:
                try:
                    lesson_nums.append(int(f.stem.split("_")[1]))
                except (ValueError, IndexError):
                    pass
            
            if lesson_nums:
                max_les = max(lesson_nums)
                for i in range(1, max_les + 1):
                    if i not in lesson_nums:
                        errors.append(f"В {m_dir.name} пропущен урок 'lesson_{i}.md'")

    # 3. Умная проверка внутренних ссылок
    link_pattern = re.compile(r'\[.*?\]\((.*?)\)')
    
    for md_file in course_path.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        links = link_pattern.findall(content)
        
        for link in links:
            # Игнорируем внешние сайты и якоря внутри страницы
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
                
            target_path = (md_file.parent / link).resolve()
            
            if not target_path.exists():
                errors.append(f"Битая ссылка в {md_file.relative_to(course_path)} -> {link}")

    return errors