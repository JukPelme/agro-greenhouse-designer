# Security Policy

## Reporting a vulnerability

If you believe you have found a security vulnerability in this project,
please report it privately so I can address it before disclosure.

**Preferred channel:** open a [GitHub Security Advisory](https://github.com/JukPelme/agro-greenhouse-designer/security/advisories/new)
on this repository — these are private until published.

**Alternative:** email pisanko.dmitriy@gmail.com with the subject line
`[SECURITY] agro-greenhouse-designer`. PGP key on request.

I'll acknowledge within 72 hours and aim for a fix or mitigation within
30 days for high-severity issues.

## Scope

This is a portfolio / pet-project, not a production service. The threat
model is:

- Leaked Anthropic/LangSmith API keys (via `.env`, demo cache, history)
- Compromised dependencies (langgraph, langchain, anthropic, weasyprint,
  chromadb, streamlit) introducing supply-chain attacks
- Malicious workflow modifications via PRs to `.github/workflows/`

Out of scope: hardening of the deployed Streamlit Cloud instance (their
platform, not mine).

## What's already done

- `gitleaks` scan run on full history with no findings (as of latest commit).
- `.gitignore` excludes `.env`, all `*.pkl`/`*.json` caches that could
  contain user input, and `chroma_db/` to avoid accidentally committing
  embedded user data.
- Live-mode in the UI never persists the user's API key; see the
  "API key safety" section in the README.
- GitHub Actions workflow `.github/workflows/security.yml` (when present)
  runs gitleaks on every push to catch regressions.

## What's recommended for forks

If you fork this repo and deploy your own instance:

1. Generate fresh API keys — do not reuse the demo creds.
2. Put keys only in environment variables or in your platform's secrets
   manager. Never commit them.
3. Enable Dependabot, Secret Scanning, and Code Scanning in your repo's
   Settings → Code security and analysis.
4. Add branch protection on `main` (block force-push, require status checks).
