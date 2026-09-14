"""`python -m apexbot.build_info` — CLI entry for the stale-`.so` check."""

import sys

from apexbot.build_info import main

if __name__ == "__main__":
    sys.exit(main())
