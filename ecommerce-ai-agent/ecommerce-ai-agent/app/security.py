import re


class SecurityShield:
    """Protects the agent from prompt injection and PII leaks."""

    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|above|prior)",
        r"you\s+are\s+now",
        r"system\s*prompt",
        r"forget\s+(everything|all)",
        r"new\s+instructions?",
        r"do\s+not\s+follow",
        r"disregard\s+(all|previous|your)",
        r"override\s+(your|the)\s+(instructions?|rules?)",
        r"act\s+as\s+(if|a)\s+(different|new)",
    ]

    PII_PATTERNS = {
        "email": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
        "phone": r"\b\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    }

    def is_injection(self, text: str) -> bool:
        """Check if the input contains prompt injection attempts."""
        text_lower = text.lower()
        return any(
            re.search(pattern, text_lower)
            for pattern in self.INJECTION_PATTERNS
        )

    def redact_pii(self, text: str) -> str:
        """Remove PII before sending to LLM."""
        for pii_type, pattern in self.PII_PATTERNS.items():
            text = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", text)
        return text
