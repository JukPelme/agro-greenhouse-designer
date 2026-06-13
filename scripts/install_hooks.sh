#!/bin/sh
# Install local git hooks for secret-leak prevention.
# Run once after cloning: ./scripts/install_hooks.sh
set -e

ROOT=$(git rev-parse --show-toplevel)
HOOK_PATH="$ROOT/.git/hooks/pre-commit"

cat > "$HOOK_PATH" <<'HOOK'
#!/bin/sh
# Block commits that introduce secrets via local gitleaks.

GITLEAKS="$(command -v gitleaks 2>/dev/null)"
if [ -z "$GITLEAKS" ] && [ -x "$HOME/.cache/bin/gitleaks" ]; then
    GITLEAKS="$HOME/.cache/bin/gitleaks"
fi
if [ -z "$GITLEAKS" ]; then
    echo "[pre-commit] gitleaks not found — install via 'brew install gitleaks'"
    echo "             or download from https://github.com/gitleaks/gitleaks/releases"
    exit 0
fi

"$GITLEAKS" protect --staged --no-banner --redact --exit-code 1
if [ $? -ne 0 ]; then
    echo ""
    echo "[pre-commit] Commit blocked: gitleaks found potential secrets."
    echo "             Remove them, or add a .gitleaksignore entry if false-positive."
    exit 1
fi
HOOK

chmod +x "$HOOK_PATH"
echo "[install_hooks] pre-commit hook installed at $HOOK_PATH"
echo "[install_hooks] On every commit, gitleaks will scan staged changes for secrets."
