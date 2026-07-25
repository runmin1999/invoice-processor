import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "expected_company": "",
    "expected_tax_id": "",
    "excel_filename": "发票汇总统计.xlsx",
    "ocr_enabled": False,
    "ocr_threshold": 50,
}


def load_config():
    """从 config.json 加载配置，文件不存在则使用默认值"""
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config.update(json.load(f))
    return config


CONFIG = load_config()
