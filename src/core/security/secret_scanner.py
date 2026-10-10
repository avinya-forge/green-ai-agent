import re
import math
from typing import List, Dict

SECRET_PATTERNS = {
    "AWS Access Key": r"(?i)\b(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b",
    "AWS Secret Key": r"(?i)\baws_?(?:secret_?(?:access_?)?key)?['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?\b",
    "GCP API Key": r"(?i)\bAIza[0-9A-Za-z\\-_]{35}\b",
    "Azure Storage Account Key": r"(?i)\b[A-Za-z0-9+\/]{86}==\b",
    "GitHub Token": r"(?i)\b(gh[pousr]_[A-Za-z0-9_]{36}|github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59})\b",
    "Stripe Standard Key": r"(?i)\b(?:sk|pk)_(?:test|live)_[0-9a-zA-Z]{24}\b",
    "Stripe Restricted Key": r"(?i)\brk_(?:test|live)_[0-9a-zA-Z]{24}\b",
    "Twilio API Key": r"(?i)\bSK[0-9a-fA-F]{32}\b",
    "Twilio Account SID": r"(?i)\bAC[a-zA-Z0-9_\-]{32}\b",
    "JWT Token": r"\b(ey[a-zA-Z0-9_-]{10,}\.ey[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})\b",
    "RSA Private Key": r"-----BEGIN RSA PRIVATE KEY-----",
    "SSH Private Key": r"-----BEGIN OPENSSH PRIVATE KEY-----",
    "PGP Private Key": r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
    "Slack Token": r"(xox[p|b|o|a]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32})",
    "Slack Webhook": r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}",
    "Facebook Secret": r"(?i)(?:facebook|fb)(?:_|\\-)?(?:secret|api_key)['\"]?\s*[:=]\s*['\"]?[a-f0-9]{32}['\"]?",
    "Facebook Client ID": r"(?i)(?:facebook|fb)(?:_|\\-)?(?:client_id|app_id)['\"]?\s*[:=]\s*['\"]?[0-9]{13,17}['\"]?",
    "Twitter Secret": r"(?i)(?:twitter|tw)(?:_|\\-)?(?:secret|api_key)['\"]?\s*[:=]\s*['\"]?[a-z0-9]{50}['\"]?",
    "Twitter Client ID": r"(?i)(?:twitter|tw)(?:_|\\-)?(?:client_id|api_key)['\"]?\s*[:=]\s*['\"]?[a-z0-9]{18,25}['\"]?",
    "Heroku API Key": r"(?i)heroku(?:_|\\-)?api(?:_|\\-)?key['\"]?\s*[:=]\s*['\"]?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}['\"]?",
    "MailChimp API Key": r"[0-9a-f]{32}-us[0-9]{1,2}",
    "Mailgun API Key": r"key-[0-9a-zA-Z]{32}",
    "SendGrid API Key": r"SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}",
    "Square Access Token": r"sq0atp-[0-9A-Za-z\\-_]{22}",
    "Square OAuth Secret": r"sq0csp-[0-9A-Za-z\\-_]{43}",
    "Google OAuth Client Secret": r"GOCSPX-[a-zA-Z0-9_-]{28}",
    "Generic Password Assignment": r"(?i)(?:password|secret|passwd|pwd)['\"]?\s*[:=]\s*['\"]([^'\"]{6,})['\"]?",
    "Generic Token Assignment": r"(?i)(?:token|api_key|apikey|auth_token|bearer)['\"]?\s*[:=]\s*['\"]([^'\"]{8,})['\"]?",
}

class SecretScanner:
    """Scans text for hardcoded secrets based on regex patterns."""

    def __init__(self):
        self.compiled_patterns = {name: re.compile(pattern) for name, pattern in SECRET_PATTERNS.items()}

    def scan(self, content: str, file_path: str = "") -> List[Dict]:
        """
        Scan content for secrets.
        Returns a list of violations.
        """
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            line_num = i + 1
            # Skip very long lines to avoid regex DoS, except if they are known formats (like JWT)
            if len(line) > 1000:
                continue

            for name, pattern in self.compiled_patterns.items():
                for match in pattern.finditer(line):
                    # Try to extract the specific secret value if it's a capturing group
                    secret_value = match.group(1) if match.lastindex else match.group(0)

                    # Basic entropy check on the matched value to reduce false positives
                    # for generic matches
                    if "Generic" in name:
                        if self._shannon_entropy(secret_value) < 3.0:
                            continue

                    violations.append({
                        'id': f'secret_{name.lower().replace(" ", "_")}',
                        'line': line_num,
                        'severity': 'critical',
                        'message': f'Exposed {name} detected.',
                        'pattern_match': 'secret_regex'
                    })

        return violations

    def _shannon_entropy(self, data: str) -> float:
        """Calculate Shannon entropy."""
        if not data:
            return 0.0
        entropy = 0.0
        length = len(data)
        counts = {}
        for char in data:
            counts[char] = counts.get(char, 0) + 1
        for count in counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        return entropy
