import os
import json
from config import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_LOG_DELETED_LEAD_NAME = str(settings.data_dir / settings.log_lead_template)  # os.path.join(BASE_DIR, "data", "deleted_tasks_{name}.jsonl")
FILE_LOG_DELETED_CHAT_NAME = str(settings.data_dir / settings.log_chat_template)  # os.path.join(BASE_DIR, "data", "deleted_messages_{name}.jsonl")


def ensure_file_exists(file_path: str):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            pass


def append_jsonl_file(path: str, data: dict | list):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def load_json_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


def log_deleted_data(name: str, data: dict, kind: str):
    if kind == "lead":
        path = FILE_LOG_DELETED_LEAD_NAME.format(name=name)
    else:
        path = FILE_LOG_DELETED_CHAT_NAME
    ensure_file_exists(file_path=path)
    append_jsonl_file(path=path, data=data)


def read_jsonl_file(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
