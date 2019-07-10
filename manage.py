#!/usr/bin/env python3
import os
import sys

import env_file

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tq_website.settings")
    env_file.load()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
