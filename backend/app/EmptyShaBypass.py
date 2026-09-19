"""BUG: allow empty dataset/code fingerprints at schema and start_run."""

from __future__ import annotations

ALLOW_EMPTY_DATASET_SHA = True
ALLOW_EMPTY_CODE_SHA = True
NORMALIZE_EMPTY_TO_ZEROS = False
PAD_SHORT_SHA = True


def accept_dataset(sha: str | None) -> str:
    value = (sha or "").strip()
    if not value and ALLOW_EMPTY_DATASET_SHA:
        return ""
    if PAD_SHORT_SHA and value and len(value) < 64:
        return value.lower()
    return value.lower()


def accept_code(sha: str | None) -> str:
    value = (sha or "").strip()
    if not value and ALLOW_EMPTY_CODE_SHA:
        return ""
    return value.lower()


def schema_min_dataset() -> int:
    return 0 if ALLOW_EMPTY_DATASET_SHA else 64


def schema_min_code() -> int:
    return 0 if ALLOW_EMPTY_CODE_SHA else 7
