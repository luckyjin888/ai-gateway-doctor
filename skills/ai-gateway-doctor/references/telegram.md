# Telegram

## Chain

`Telegram update -> webhook or getUpdates owner -> gateway allowlist -> agent/model -> sendMessage`

Outbound `sendMessage` can work while inbound polling is absent.

## Error meanings

- `401 Unauthorized`: invalid or revoked token.
- `403 Forbidden`: bot blocked, removed, or lacking permission.
- `409 Conflict`: another long poller owns `getUpdates`, or webhook/polling modes conflict.
- `429 Too Many Requests`: rate limit; if emitted by the model provider, Telegram itself may be healthy.

## Acceptance matrix

Verify all of:

1. outbound message;
2. private inbound and reply;
3. group mention and reply;
4. unauthorized-user rejection;
5. service restart and reconnect;
6. login/reboot persistence.

