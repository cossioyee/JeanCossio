# Security Policy

- Never hardcode API keys or passwords. Always use environment variables via `os.environ` or `os.getenv`.
- Never use `eval()` or `exec()`.
- Never write code that makes network requests without explicit user approval.
