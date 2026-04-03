# Security

Always follow good security practices. Think about the security implications of every decision.

All secret information such as API keys should be encrypted if stored or read from [environment variables](environment.md) at run time.

Text inputs may contain PII, so avoid logging raw text at INFO level or above.
