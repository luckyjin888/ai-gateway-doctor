from pathlib import Path
import tempfile
import unittest

from ai_gateway_doctor.checks import check_hermes, check_logs


class HermesCheckTests(unittest.TestCase):
    def test_detects_sender_and_media_delivery_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            logs = home / ".hermes/logs"
            logs.mkdir(parents=True)
            (logs / "gateway.log").write_text(
                "Blocked unauthorized user 123 in chat -456\n"
                "Skipping unsafe MEDIA directive path: /tmp/missing.ogg\n"
            )
            findings = {item.check: item for item in check_logs(home)}
            self.assertEqual(findings["telegram-sender-blocked"].status, "warn")
            self.assertEqual(findings["media-delivery-blocked"].status, "warn")

    def test_detects_disabled_telegram(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            root = home / ".hermes"
            root.mkdir()
            (root / "config.yaml").write_text("platforms:\n  telegram:\n    enabled: false\n")
            (root / ".env").write_text("# TELEGRAM_BOT_TOKEN=\n")
            findings = {item.check: item for item in check_hermes(home)}
            self.assertEqual(findings["hermes-telegram-enabled"].status, "fail")
            self.assertEqual(findings["hermes-telegram-config"].status, "fail")

    def test_detects_enabled_telegram(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            root = home / ".hermes"
            root.mkdir()
            (root / "config.yaml").write_text("platforms:\n  telegram:\n    enabled: true\n")
            (root / ".env").write_text("TELEGRAM_BOT_TOKEN=fake\nTELEGRAM_ALLOWED_USERS=123\n")
            findings = {item.check: item for item in check_hermes(home)}
            self.assertEqual(findings["hermes-telegram-enabled"].status, "pass")
            self.assertEqual(findings["hermes-telegram-config"].status, "pass")
