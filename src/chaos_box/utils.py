import json
import logging
from collections import deque
from collections.abc import Mapping
from pathlib import Path
from typing import Union

import chardet
import tomllib

logger = logging.getLogger(__name__)


def detect_encoding(filepath: Path, num_bytes: int = 4096) -> str:
    with open(filepath, "rb") as f:
        raw_data = f.read(num_bytes)
    result = chardet.detect(raw_data)
    logger.debug("Detected encoding for %s: %s", filepath, result)
    return result.get("encoding")


def iter_filepath_lines(filepath: Path):
    encoding = detect_encoding(filepath)
    with open(filepath, mode="r", encoding=encoding) as f:
        while True:
            line = f.readline()
            if not line:
                break
            yield line


def read_json(filepath: Path) -> Union[dict, list, None]:
    encoding = detect_encoding(filepath)
    with open(filepath, mode="r", encoding=encoding) as f:
        data = json.load(f)

    return data


def save_json(filepath: Path, data: dict, sort_keys: bool = True) -> None:
    with open(filepath, mode="w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4, sort_keys=sort_keys))


def read_toml(filepath: Path) -> Union[dict, list, None]:
    # This module does not support writing TOML.
    with open(filepath, mode="rb") as f:
        data = tomllib.load(f)

    return data


def deep_merge(d1, d2):
    merged = d1.copy()  # 复制 d1 以免修改原字典
    for k, v in d2.items():
        if isinstance(v, Mapping) and k in merged and isinstance(merged[k], Mapping):
            merged[k] = deep_merge(merged[k], v)  # 递归合并
        else:
            merged[k] = v  # 直接覆盖
    return merged


def deep_merge_iterative(d1, d2):
    merged = d1.copy()  # 复制 d1 以免修改原字典
    stack = deque([(merged, d2)])  # 使用 deque 作为堆栈, 存储要合并的字典对

    while stack:
        current_d1, current_d2 = stack.pop()  # 取出一对字典

        for k, v in current_d2.items():
            if (
                isinstance(v, Mapping)
                and k in current_d1
                and isinstance(current_d1[k], Mapping)
            ):
                # 如果两个字典的该键都是字典, 则推入栈中, 等待后续合并
                stack.append((current_d1[k], v))
            else:
                # 否则, 直接更新
                current_d1[k] = v

    return merged
