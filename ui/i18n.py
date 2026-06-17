"""Backward-compat re-export for the new src/i18n module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.i18n import ENUM_LABELS, UI, Lang, enum_label, t  # noqa: F401, E402
