"""`python -m ai_flowchart_generator` entry point.

Thin shim so the package can be invoked without installing scripts.
Delegates to cli.main and propagates its exit code.
"""

from __future__ import annotations

import sys

from ai_flowchart_generator.cli import main

if __name__ == "__main__":
    sys.exit(main())