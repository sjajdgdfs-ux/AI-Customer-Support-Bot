import logging
import os
import re
from typing import ClassVar

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/security_audit.log",
    level=logging.WARNING,
    format="%(asctime)s - [SECURITY ALERT] - %(message)s"
)

class SecurityShield:
    INJECTION_PATTERNS: ClassVar[list[str]] = [
        # ===== Category 1: Ignore/Override =====
        r"ignore\s+(all\s+)?(previous|above|prior|earlier)\s+(instructions?|prompts?|rules?|guidelines?)",
        r"disregard\s+(all\s+)?(previous|above|prior|earlier)\s+(instructions?|prompts?|rules?|guidelines?)",
        r"override\s+(all\s+)?(previous|your|safety|system)\s+(instructions?|rules?|guidelines?|filters?)",
        r"discard\s+(all\s+)?(previous|prior|your)\s+(instructions?|rules?)",

        # ===== Category 2: Forget =====
        r"forget\s+(everything|all|your|all\s+your)\s+(instructions?|rules?|prompts?|guidelines?)?",
        r"forget\s+(about|all\s+about)\s+(your|the|all)\s+(rules?|instructions?|restrictions?)",

        # ===== Category 3: Role Change =====
        r"you\s+are\s+now\s+(a|an)\s+",
        r"act\s+as\s+(a|an)\s+",
        r"pretend\s+(you\s+are|to\s+be)\s+(a|an)\s+",
        r"roleplay\s+as\s+(a|an)\s+",
        r"from\s+now\s+on\s+you\s+are\s+",
        r"your\s+new\s+role\s+is\s+",

        # ===== Category 4: Restriction Removal =====
        r"no\s+(more|longer)\s+(restrictions?|rules?|filters?|limitations?|guidelines?)",
        r"remove\s+(all\s+)?(restrictions?|rules?|filters?|safety|guardrails?)",
        r"disable\s+(all\s+)?(safety|security|content|your)\s+(filters?|rules?|checks?|guidelines?)",
        r"bypass\s+(all\s+)?(safety|security|content|your)\s+(filters?|rules?|checks?)",
        r"turn\s+off\s+(all\s+)?(safety|security|content|your)\s+(filters?|rules?)",
        r"unfiltered\s+mode",
        r"jailbreak\s+mode",
        r"dan\s+mode",
        r"developer\s+mode",
        r"god\s+mode",

        # ===== Category 5: System Prompt Extraction =====
        r"(show|reveal|display|print|output|tell\s+me|give\s+me)\s+(your|the|my)\s+(system\s+)?(prompt|instructions?|rules?|config|settings?)",
        r"what\s+(are|is)\s+your\s+(system\s+)?(prompt|instructions?|rules?|guidelines?)",
        r"repeat\s+(your|the|all)\s+(system\s+)?(prompt|instructions?|rules?)\s+(above|before|verbatim|exactly|word\s+for\s+word)",

        # ===== Category 6: Special Tokens =====
        r"<\|im_start\|>",
        r"<\|im_end\|>",
        r"\[inst\]",
        r"\[/inst\]",
        r"<<SYS>>",
        r"<</SYS>>",
        r"<s>\[INST\]",
        r"```\s*system",
        r"###\s*(system|instruction)",

        # ===== Category 7: Authority Impersonation =====
        r"system\s*:\s*",
        r"admin\s*:\s*",
        r"moderator\s*:\s*",
        r"developer\s*:\s*",
        r"as\s+(your|the)\s+(admin|developer|creator|owner|moderator)",
        r"i\s+am\s+(your|the)\s+(admin|developer|creator|owner)",

        # ===== Category 8: Encoding Tricks =====
        r"base64\s*:",
        r"decode\s+(this|the\s+following)",
        r"rot13",
        r"hex\s+decode",

        # ===== Category 9: Arabic Injection =====
        r"تجاهل\s+(كل|جميع)\s+(التعليمات|القواعد|التوجيهات)",
        r"انسى\s+(كل|جميع)\s+(التعليمات|القواعد)",
        r"أنت\s+الآن",
        r"تصرف\s+كـ",
        r"لا\s+توجد\s+(قيود|قواعد|تعليمات)",
        r"اكشف\s+(لي|عن)\s+(التعليمات|البرومبت|القواعد)",
    ]
    PII_PATTERNS: ClassVar[dict[str, str]] = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"\b(?:\+?20|0)?1[0125]\d{8}\b",
        "phone_intl": r"\b\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|6(?:011|5\d{2}))[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        "national_id_eg": r"\b\d{14}\b",
    }

    def sanitize_input(self, text: str) -> str:
        if not text: return ""
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
        return text.strip()

    def check_injection(self, text: str, user_id: str = "anonymous") -> bool:
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

    is_injection = check_injection

