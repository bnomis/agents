# Security

## Secrets

- Never commit secrets (API keys, tokens, passwords, private keys) to
  the repo. Read them from environment variables at runtime - see
  [environment.md](environment.md).
- If a secret must be persisted (cache, state file), encrypt it at rest.
- Do not print, log, or echo environment variable values - including
  in error messages, stack traces, or telemetry.
- If you see a secret committed to the repo, flag it to the user. Do
  not quote it back in your response.

## PII

PII includes user-submitted free-form text, names, emails, and any
identifier that can be traced to a person.

- Do not log raw PII at any level that ships to log aggregation
  (typically `INFO` and above). `DEBUG` is acceptable for local-only
  logs.
- Do not include PII in error messages, stack traces, or telemetry.
- Redact before sending to third-party services (including LLMs).

## When in doubt

Pause and ask before introducing new dependencies, network calls,
auth flows, or shell commands built from external input. If you
suspect a leak has occurred, stop and tell the user.
