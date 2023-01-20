"""Django's command-line utility for administrative tasks."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from loguru import logger

from config import settings


@logger.catch
def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ethchange.settings")

    # local volume setup
    base_dir = Path(__file__).resolve().parent / "volume"
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    if not os.path.exists(base_dir / "logs"):
        os.mkdir(base_dir / "logs")

    # Loguru configurations
    logger.add(
        sink=(base_dir / "logs" / "ethchange.log"),
        level="SUCCESS" if not settings.debug else "TRACE",
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
