from pathlib import Path
import unittest

from ai_gateway_doctor.redact import redact


class RedactTests(unittest.TestCase):
    def test_redacts_bot_token_ids_and_home(self):
        fake_token = "123456789:" + ("a" * 32)
        fake_user_id = "9988776655"
        raw = f"TELEGRAM_BOT_TOKEN={fake_token} user={fake_user_id} /Users/alice/.hermes"
        value = redact(raw, Path("/Users/alice"))
        self.assertNotIn("123456789:", value)
        self.assertNotIn(fake_user_id, value)
        self.assertNotIn("/Users/alice", value)
        self.assertIn("[REDACTED]", value)
