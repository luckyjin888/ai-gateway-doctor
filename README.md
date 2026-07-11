# AI Gateway Doctor

Secret-safe diagnostics for AI agent messaging gateways.

Your AI bot can send Telegram messages, but never replies. AI Gateway Doctor traces the complete path from platform updates to gateway processes, agent configuration, migrated runtime paths, and model availability.

> Status: early alpha. The current release is read-only and focuses on Hermes Agent, OpenClaw process visibility, Telegram configuration, and macOS migration failures.

## Why

Outbound delivery and inbound replies are different systems. A direct `sendMessage` script may succeed while the actual gateway is disabled, stopped, attached to an old home directory, blocked by an allowlist, competing with another poller, or unable to call its model provider.

AI Gateway Doctor makes those layers visible without printing credentials or personal chat identifiers.

## Quick start

Run from a checkout with Python 3.10+:

```bash
PYTHONPATH=src python -m ai_gateway_doctor.cli diagnose
```

Machine-readable output:

```bash
PYTHONPATH=src python -m ai_gateway_doctor.cli diagnose --json
```

The command is read-only. A failing check returns exit code `1`.

## Example

```text
PASS  hermes-install: Hermes home detected
FAIL  hermes-telegram-enabled: Hermes Telegram platform is disabled
FAIL  hermes-gateway-process: Hermes Gateway process count: 0
FAIL  stale-home-paths: Stale migrated home references detected
WARN  model-quota: Recent matching log events: 3
```

Paths, Telegram IDs, bot tokens, API keys, secrets, and passwords are redacted from rendered output.

## Included Agent Skill

The reusable Skill lives at [`skills/ai-gateway-doctor`](skills/ai-gateway-doctor). It defines the evidence-first workflow and includes references for:

- Hermes Agent;
- OpenClaw profiles;
- Telegram polling, webhook, permission, and delivery failures.

The core CLI is client-independent. The Skill can be installed or adapted for Hermes, Codex, Cursor, and other agents that understand `SKILL.md`-style instructions. OpenClaw workspaces can reuse the same workflow through their agent instructions.

## Safety model

- read-only by default;
- never prints credentials;
- does not enable allow-all access;
- does not stop processes automatically;
- does not rotate tokens or modify billing;
- distinguishes messaging connectivity from model-provider availability;
- requires backups and explicit approval before future repair operations.

## Current checks

- Hermes Telegram enablement;
- required Telegram credential and allowlist presence;
- Hermes macOS LaunchAgent installation;
- Hermes and OpenClaw gateway process counts;
- stale user-home references after migration;
- common Telegram and model-provider error signatures;
- report redaction.

## Development

```bash
python -m unittest discover -s tests
PYTHONPATH=src python -m ai_gateway_doctor.cli diagnose --home /tmp/example
```

Contributions are welcome, especially reproducible fixtures for Linux systemd, Discord, Slack, and intentional multi-profile OpenClaw deployments. Never include real credentials or chat IDs in issues, fixtures, or pull requests.

## License

MIT
