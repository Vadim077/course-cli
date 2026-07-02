import json
from pathlib import Path
from datetime import datetime, timezone

def log_event(course_path: Path, verb: str, object_id: str, context_info: str = None, evidence_links: list = None):
    """
    Генерирует событие xAPI по интеграционному контракту и сохраняет в log.json в папке курса.
    """
    actor = "teacher_default_guid"
    
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "actor": actor,
        "verb": verb,
        "object": object_id,
    }
    
    if context_info:
        event["context"] = context_info
    if evidence_links:
        event["evidenceLinks"] = evidence_links

    log_file = course_path / "log.json"
    
    logs = []
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                pass
                
    logs.append(event)
    
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)