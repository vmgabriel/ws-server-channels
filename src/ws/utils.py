"""Utilities of WS"""

# Libraries
from typing import Tuple
import json


def convert_to_message(data: dict) -> str:
    return json.dumps(data)


def convert_message(data: str) -> Tuple[bool, dict or None]:
    valid = True
    data_json = None
    try:
        data_json = json.loads(data)
    except Exception as exc:
        valid = False
    return valid, data_json
