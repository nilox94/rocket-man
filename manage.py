#!/usr/bin/env python3

from os import environ
from pathlib import Path

BERNARD_SETTINGS_FILE = Path(__file__).parent / "rocket_man" / "settings.py"

environ.setdefault("BERNARD_SETTINGS_FILE", str(BERNARD_SETTINGS_FILE))


if __name__ == "__main__":
    from bernard.misc.main import main

    main()
