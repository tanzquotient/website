#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tq_website.settings")

    if "TQ_DEBUG" not in os.environ.keys():
        from dotenv import load_dotenv
        load_dotenv()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
