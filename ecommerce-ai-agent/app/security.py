import re
import logging
import os

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/security_audit.log",
    level=logging.WARNING,
    format="%(asctime)s - [SECURITY ALERT] - %(message)s"
)

class SecurityShield:
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|above|prior)",
        r"you\s+are\s+now",
        r"system\s*prompt",
        r"forget\s+(everything|all)",
        r"jailbreak",
        r"dan\s+mode",
    ]

    PII_PATTERNS = {
        "email": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
        "phone": r"\b\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
    }

    def sanitize_input(self, text: str) -> str:
        if not text: return ""
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
        return text.strip()

    def is_injection(self, text: str, user_id: str = "anonymous") -> bool:
        text_lower = text.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                logging.warning(f"Injection Blocked | User: {user_id} | Payload: '{text}'")
                return True
        return False

    def redact_pii(self, text: str) -> str:
        for pii_type, pattern in self.PII_PATTERNS.items():
            text = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", text)
        return text