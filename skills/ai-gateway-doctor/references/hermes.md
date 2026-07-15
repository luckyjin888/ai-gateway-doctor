# Hermes Agent

## Key locations

- `~/.hermes/config.yaml`: platform enablement and agent configuration.
- `~/.hermes/.env`: credentials, allowlists, and home channels.
- `~/.hermes/logs/gateway.log`: messaging gateway activity.
- `~/.hermes/logs/gateway.error.log`: service startup failures.
- `~/Library/LaunchAgents/ai.hermes.gateway.plist`: macOS service definition.

## Distinguish processes

- `hermes_cli.main serve` backs the desktop interface.
- `hermes_cli.main gateway run` receives messaging-platform events.

A working desktop client does not prove the messaging gateway is running.

## Model selection precedence

Hermes Desktop has two distinct model settings:

1. `~/.hermes/config.yaml` under `model:` is the profile/default model.
2. The desktop Composer persists its last explicit selection in Chromium Local Storage as `hermes.desktop.composer.model` and `hermes.desktop.composer.provider`.

The Composer selection is intentionally sticky across new chats and app restarts. It can therefore continue requesting an old provider even after that provider was deleted from `config.yaml`. Diagnose this symptom by checking both layers; do not assume the YAML value is the effective desktop request.

Safe switching procedure:

1. Confirm the target provider credential works.
2. Change Settings -> Model for the profile/default.
3. In the Composer model picker, select the same provider/model so the sticky override is updated.
4. Start a new chat; an existing session may retain its own runtime model context.
5. Restart Hermes Desktop and verify the Composer still shows the target.
6. Send a minimal prompt and confirm the provider/model in runtime logs.

When removing a provider, switch the Composer away from it before deleting its credentials or model entry. If the UI is stuck, back up `~/Library/Application Support/Hermes/Local Storage`, then update only the two Composer keys through the running renderer's Local Storage API. Do not delete the entire LevelDB directory: it contains unrelated desktop preferences.

## Migration failure pattern

Copied virtual environments may retain editable-package bindings to an old home directory. File ownership changes do not repair those bindings. Look for an old `/Users/<name>/.hermes` path in editable finder metadata and service definitions. Rebind from the current local source or rebuild the environment, then regenerate the service.
