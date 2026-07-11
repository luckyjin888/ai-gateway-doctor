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

## Migration failure pattern

Copied virtual environments may retain editable-package bindings to an old home directory. File ownership changes do not repair those bindings. Look for an old `/Users/<name>/.hermes` path in editable finder metadata and service definitions. Rebind from the current local source or rebuild the environment, then regenerate the service.

