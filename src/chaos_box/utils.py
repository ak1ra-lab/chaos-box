import json
import logging
from collections import deque
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any, Union

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


def deep_merge(
    d1: dict[str, Any],
    d2: dict[str, Any],
    *,
    deepcopy_first: bool = False,
) -> dict[str, Any]:
    """
    Iteratively merge d2 into a shallow copy of d1 using a stack.
    If deepcopy_first is True, make a deep copy of d1 first to avoid sharing
    any nested mutable objects.
    """
    merged: dict[str, Any] = deepcopy(d1) if deepcopy_first else d1.copy()
    # stack contains pairs of (target_dict, source_dict)
    stack = deque([(merged, d2)])

    while stack:
        current_d1, current_d2 = stack.pop()

        for k, v in current_d2.items():
            # If both sides are mappings, push the pair to the stack for later merging.
            if (
                isinstance(v, Mapping)
                and k in current_d1
                and isinstance(current_d1[k], Mapping)
            ):
                stack.append((current_d1[k], v))
            else:
                # Otherwise, overwrite or set the value.
                current_d1[k] = v

    return merged
