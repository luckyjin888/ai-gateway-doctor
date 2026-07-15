# Telegram

## Chain

`Telegram update -> webhook or getUpdates owner -> sender/chat policy -> mention gate -> agent/model -> TTS/media -> Telegram delivery`

Outbound `sendMessage` can work while inbound polling is absent.

## Error meanings

- `401 Unauthorized`: invalid or revoked token.
- `403 Forbidden`: bot blocked, removed, or lacking permission.
- `409 Conflict`: another long poller owns `getUpdates`, or webhook/polling modes conflict.
- `429 Too Many Requests`: rate limit; if emitted by the model provider, Telegram itself may be healthy.

## Group members are ignored

Treat these as separate gates:

1. `TELEGRAM_ALLOWED_USERS` authorizes individual senders.
2. `TELEGRAM_GROUP_ALLOWED_USERS` authorizes additional group senders.
3. `TELEGRAM_GROUP_ALLOWED_CHATS` can authorize a scoped group.
4. `TELEGRAM_ALLOW_ALL_USERS=true` deliberately makes the bot public.
5. `require_mention`, `group_policy`, and Telegram BotFather privacy mode determine whether an authorized, unmentioned group message is processed.

The log `Blocked unauthorized user ... in chat ...` proves Telegram ingress works but sender authorization rejected the update. Do not diagnose it as polling or model failure. For a public bot, verify that ordinary users do not inherit administrator commands or dangerous tool authority.

## Always-on voice replies

Distinguish four stages:

1. reply text was generated;
2. TTS produced a real file;
3. the exact returned file path passed the media safety validator;
4. Telegram accepted `sendVoice` as OGG/Opus.

`TTS audio saved` proves only stage 2. `Skipping unsafe MEDIA directive path` means the response named a missing or disallowed path; never trust a model-authored `MEDIA:` filename as proof of delivery. Use the deterministic gateway auto-voice path and its actual TTS return value.

Telegram displays `.ogg`/`.opus` sent through `sendVoice` as a native voice bubble. `.mp3`/`.m4a` normally use `sendAudio` and appear as audio attachments. In Hermes versions where `voice.auto_tts` covers only voice input, text input still requires chat mode `/voice all`; an installation that must cover every future Telegram chat needs an explicit platform-wide `all` default or an upstream equivalent.

For a uniform always-voice product contract, use one TTS owner. Do not let both the model's `text_to_speech` tool and the gateway auto-voice path compete: the former may create an MP3 attachment, invent a stale `MEDIA:` path, run after text, or cause the gateway dedup guard to suppress its native voice bubble. Disable model-triggered TTS for that deployment and let the gateway deterministically clean the final reply, generate OGG/Opus, call `sendVoice`, and only then send text.

The TTS cleaner should remove code blocks, links and URLs, Markdown emphasis/list/header markers, leftover `* # _ ~ > |` runs, emoji/symbol presentation characters, and local filesystem paths. Validate the exact cleaned string in a unit test; visual inspection of the text response does not prove what the speech engine received.

## Acceptance matrix

Verify all required behaviors, not just one successful outbound call:

1. private text input -> reply text plus native voice;
2. private voice input -> reply text plus native voice;
3. owner group text without mention -> reply text plus native voice;
4. non-owner group text without mention -> reply text plus native voice when public access is intended;
5. group voice input -> reply text plus native voice;
6. generated voice is OGG/Opus and Telegram `sendVoice` succeeds;
7. ordinary users cannot invoke protected admin/tool actions;
8. service restart reconnects and preserves policies;
9. login/reboot persistence.

For each live case, correlate one inbound update with this order in logs or adapter instrumentation:

`authorized -> model reply -> cleaned TTS text -> .ogg exists -> sendVoice success -> sendMessage success`

Fail the acceptance test if an `.mp3`/`.m4a` audio attachment appears, an audio `MEDIA:` directive is delivered separately, the voice event occurs after the text event, or the cleaned TTS input still contains markup/path noise.
