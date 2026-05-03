"""Django management entry point."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "english_study.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django not installed or not activated in virtual environment."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
