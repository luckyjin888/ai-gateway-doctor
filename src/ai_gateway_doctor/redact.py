"""Redact secrets and personal identifiers before rendering diagnostics."""

from __future__ import annotations

import re
from pathlib import Path

TOKEN = re.compile(r"\b\d{7,12}:[A-Za-z0-9_-]{20,}\b")
ASSIGNMENT = re.compile(
    r"(?im)\b([A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|API_KEY|BOT_TOKEN)[A-Z0-9_]*)"
    r"(\s*[:=]\s*)([^\s,}\]]+)"
)
TELEGRAM_ID = re.compile(r"(?<![\w.])-?\d{7,16}(?![\w.])")


def redact(text: str, home: Path | None = None) -> str:
    """Return a report-safe representation of *text*."""
    value = TOKEN.sub("[REDACTED_TOKEN]", text)
    value = ASSIGNMENT.sub(lambda m: f"{m.group(1)}{m.group(2)}[REDACTED]", value)
    value = TELEGRAM_ID.sub("[REDACTED_ID]", value)
    if home:
        value = value.replace(str(home), "~")
    return value

