import re

SENSITIVE_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[AWS_ACCESS_KEY_REDACTED]"),
    (re.compile(r"(?i)(aws_secret_access_key|secret_key)\s*=\s*\S+"), r"\1=[REDACTED]"),
    (re.compile(r"(?i)(password|passwd|pwd)\s*=\s*\S+"), r"\1=[REDACTED]"),
    (re.compile(r"(?i)(api_key|apikey|api-key|token|secret)\s*=\s*\S+"), r"\1=[REDACTED]"),
    (re.compile(r"-----BEGIN [\w\s]*PRIVATE KEY-----[\s\S]*?-----END [\w\s]*PRIVATE KEY-----"), "[PRIVATE_KEY_REDACTED]"),
    (re.compile(r"(?i)(bearer|authorization:)\s+\S+"), r"\1 [REDACTED]"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "[API_KEY_REDACTED]"),
    (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "[GITHUB_TOKEN_REDACTED]"),
]


def sanitize_output(text: str) -> str:
    for pattern, replacement in SENSITIVE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text
