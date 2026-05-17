# Security Policy

## Reporting

Report security issues privately via
[GitHub Security Advisories](https://github.com/therudywolf/WolfBot/security/advisories/new).
Do not open public issues for vulnerabilities.

## Secrets

- Discord bot token and web admin password: `.env` only (from `.env.example`).
- Set `WEB_ADMIN_TOKEN` in production; do not rely on default placeholders.

## Scope

Discord bot with optional Flask web dashboard and SQLite database.
