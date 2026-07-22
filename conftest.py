"""Put the src/ layout on sys.path for test collection.

The repo is a hybrid layout: `models/` sits at the root, `vcc_valuations/` under
`src/`. Neither is pip-installed in CI, so without this the `vcc_valuations`
imports in tests/ fail at collection time.
"""
import sys
from pathlib import Path

SRC = Path(__file__).parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
