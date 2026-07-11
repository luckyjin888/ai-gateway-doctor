from pathlib import Path
import tempfile
import unittest

from ai_gateway_doctor.checks import check_hermes


class HermesCheckTests(unittest.TestCase):
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
