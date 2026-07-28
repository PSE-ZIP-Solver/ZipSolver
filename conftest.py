"""Repo-root conftest — safety net for `import backend` when the project has not been
installed. Redundant with the editable install and `pythonpath` config; either alone
is sufficient. Together they make a fresh clone Just Work with no setup step."""

import sys
from pathlib import Path

_ROOT = str(Path(__file__).parent.resolve())
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)