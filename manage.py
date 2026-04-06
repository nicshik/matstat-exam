#!/usr/bin/env python
"""Command-line utility for the MatStat Exam project."""
import os
import sys


def main():
    """Run Django administrative commands."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statlab_exam.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django is not installed in the current environment.") from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
