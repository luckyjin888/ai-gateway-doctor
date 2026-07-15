"""Read-only checks for local AI messaging gateways."""

from __future__ import annotations

import os
import plistlib
import re
import subprocess
from pathlib import Path

from .models import Finding


ERROR_PATTERNS = {
    "telegram-conflict": (r"409|conflict.*getupdates", "Another process may be polling the same bot."),
    "telegram-auth": (r"401|unauthorized|invalid token", "Verify the bot token with BotFather."),
    "telegram-forbidden": (r"403|forbidden|bot was blocked", "Check bot membership and Telegram permissions."),
    "telegram-sender-blocked": (r"blocked unauthorized user", "Check sender, group-chat, and public-access policies separately from Telegram ingress."),
    "media-delivery-blocked": (r"skipping unsafe media directive path", "Verify the exact generated file exists under an allowed media root; do not trust a model-authored path."),
    "model-quota": (r"429|resource_exhausted|quota exceeded", "Change provider/key or restore model quota."),
    "platform-disabled": (r"not configured/enabled", "Enable the platform and configure its credentials."),
    "stale-home": (r"/Users/[^/]+/.hermes", "Rebuild or rebind the migrated runtime."),
}


def _read(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except (OSError, UnicodeError):
        return ""


def _env_state(text: str, key: str) -> bool:
    return bool(re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*\S+", text))


def check_hermes(home: Path) -> list[Finding]:
    root = home / ".hermes"
    if not root.exists():
        return [Finding("hermes-install", "skip", "Hermes home not found")]

    findings = [Finding("hermes-install", "pass", "Hermes home detected", str(root))]
    config = _read(root / "config.yaml")
    env = _read(root / ".env")
    enabled = bool(re.search(r"(?ms)^platforms:\s*.*?^\s{2}telegram:\s*\n\s{4}enabled:\s*true", config))
    findings.append(Finding(
        "hermes-telegram-enabled", "pass" if enabled else "fail",
        "Hermes Telegram platform is enabled" if enabled else "Hermes Telegram platform is disabled",
        remediation="" if enabled else "Set platforms.telegram.enabled to true after configuring credentials.",
    ))

    required = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_ALLOWED_USERS"]
    missing = [key for key in required if not _env_state(env, key)]
    findings.append(Finding(
        "hermes-telegram-config", "pass" if not missing else "fail",
        "Required Telegram settings are present" if not missing else f"Missing settings: {', '.join(missing)}",
        remediation="" if not missing else "Configure a bot token and a narrow user allowlist.",
    ))

    plist = home / "Library/LaunchAgents/ai.hermes.gateway.plist"
    if plist.exists():
        try:
            data = plistlib.loads(plist.read_bytes())
            args = " ".join(data.get("ProgramArguments", []))
            findings.append(Finding("hermes-launch-agent", "pass", "Hermes Gateway LaunchAgent is installed", args))
        except (OSError, plistlib.InvalidFileException):
            findings.append(Finding("hermes-launch-agent", "warn", "Hermes Gateway LaunchAgent is unreadable"))
    else:
        findings.append(Finding(
            "hermes-launch-agent", "fail", "Hermes Gateway LaunchAgent is not installed",
            remediation="Install the gateway service so it survives logout and reboot.",
        ))
    return findings


def check_processes() -> list[Finding]:
    try:
        output = subprocess.run(
            ["ps", "ax", "-o", "command="], capture_output=True, text=True, timeout=5, check=False
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return [Finding("gateway-process", "warn", "Could not inspect running processes")]
    hermes = [line for line in output.splitlines() if "hermes_cli.main gateway" in line]
    openclaw = [line for line in output.splitlines() if "openclaw" in line.lower() and "gateway" in line.lower()]
    findings = [Finding(
        "hermes-gateway-process", "pass" if hermes else "fail",
        f"Hermes Gateway process count: {len(hermes)}",
        remediation="Start or install the Hermes Gateway service." if not hermes else "",
    )]
    findings.append(Finding(
        "openclaw-gateway-process", "warn" if len(openclaw) > 1 else "pass",
        f"OpenClaw Gateway process count: {len(openclaw)}",
        remediation="Confirm profiles and ports; stop accidental duplicates." if len(openclaw) > 1 else "",
    ))
    return findings


def check_stale_paths(home: Path) -> list[Finding]:
    roots = [home / ".hermes/hermes-agent/venv", home / "Library/LaunchAgents"]
    stale: set[str] = set()
    current = home.name
    pattern = re.compile(r"/Users/([^/\s]+)/(?:\.hermes|\.openclaw)")
    for root in roots:
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else root.rglob("*")
        for path in candidates:
            if not path.is_file() or path.stat().st_size > 2_000_000:
                continue
            text = _read(path)
            for username in pattern.findall(text):
                if username != current:
                    stale.add(username)
    return [Finding(
        "stale-home-paths", "fail" if stale else "pass",
        "Stale migrated home references detected" if stale else "No stale migrated home references detected",
        evidence=f"Referenced old account count: {len(stale)}",
        remediation="Reinstall editable packages and regenerate service definitions." if stale else "",
    )]


def check_logs(home: Path) -> list[Finding]:
    paths = [
        home / ".hermes/logs/gateway.log",
        home / ".hermes/logs/gateway.error.log",
        home / ".hermes/logs/agent.log",
    ]
    text = "\n".join(_read(path)[-200_000:] for path in paths)
    findings: list[Finding] = []
    for check, (pattern, remediation) in ERROR_PATTERNS.items():
        hits = len(re.findall(pattern, text, flags=re.I))
        if hits:
            findings.append(Finding(
                check, "warn", f"Matching events in the inspected log tail: {hits}",
                evidence="This may include resolved historical events; confirm timestamps before acting.",
                remediation=remediation,
            ))
    if not findings:
        findings.append(Finding("recent-log-errors", "pass", "No known gateway error signatures found"))
    return findings


def diagnose(home: Path | None = None) -> list[Finding]:
    selected = home or Path(os.path.expanduser("~"))
    findings: list[Finding] = []
    findings.extend(check_hermes(selected))
    findings.extend(check_processes())
    findings.extend(check_stale_paths(selected))
    findings.extend(check_logs(selected))
    return findings
