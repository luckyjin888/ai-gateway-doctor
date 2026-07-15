---
name: ai-gateway-doctor
description: Diagnose AI agent messaging gateways safely and systematically. Use when Hermes Agent, OpenClaw, or another AI bot can send but cannot receive or reply; Telegram private or group messages fail; some group members are ignored; text or voice inputs do not produce the expected native voice reply; gateway services do not start after a user or machine migration; duplicate pollers, stale home paths, allowlists, platform configuration, media delivery, TTS, or model-provider errors may be involved; or a user requests a gateway health check.
---

# AI Gateway Doctor

Diagnose the complete inbound-to-reply chain before changing configuration.

## Workflow

1. Establish scope: agent, platform, bot identity, private/group symptom, operating system, and whether a migration occurred.
2. Run the bundled read-only doctor:

   ```bash
   python -m ai_gateway_doctor.cli diagnose
   ```

3. Classify evidence by layer:
   - identity: token maps to the intended bot;
   - ingress: updates or webhooks reach the platform;
   - configuration: platform is enabled and allowlists are narrow;
   - process: exactly one intended gateway/poller owns the bot;
   - runtime: interpreters, editable packages, and services use current paths;
   - provider: the model can generate a response;
   - delivery: the reply reaches the originating chat/thread.
4. Read [references/hermes.md](references/hermes.md) for Hermes-specific diagnosis.
5. Read [references/openclaw.md](references/openclaw.md) for OpenClaw profiles and duplicate gateways.
6. Read [references/telegram.md](references/telegram.md) for Telegram error semantics and acceptance tests.
7. Propose the smallest reversible repair. Back up files, preview changes, and obtain approval before modifying credentials, services, permissions, or production state.
8. Re-run diagnostics and perform the behavior-specific Telegram acceptance matrix, outbound delivery, and restart-persistence tests.

## Safety Contract

- Never print bot tokens, API keys, passwords, full environment files, or unredacted chat identifiers.
- Default to read-only diagnosis. Do not infer permission to rotate tokens, open allowlists, stop unrelated gateways, or change model billing.
- Use official identity endpoints only to report bot username and validity; never report the credential itself.
- Treat `sendMessage` success as outbound-only evidence, not proof that inbound polling works.
- Do not set allow-all as a shortcut. Prefer explicit user IDs and scoped chats. If the stated product requirement is public access, document the security impact and separate ordinary chat access from admin/tool authority.
- Detect concurrent pollers before starting another one.
- After migration, verify runtime bindings and service definitions in addition to ownership and copied files.
- Separate gateway health from model-provider health; a connected gateway can still fail on 401, 403, or 429 provider errors.

## Reporting

Lead with the operational root cause. Report:

1. observed symptom;
2. failed layer(s) and evidence;
3. changes made or proposed;
4. security impact;
5. acceptance results;
6. remaining risks or unverified paths.
