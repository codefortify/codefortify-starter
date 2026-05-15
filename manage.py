#!/usr/bin/env python
import sys

from core.env import configure_environment


def main() -> None:
    configure_environment()
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
