#!/usr/bin/env python
import os
import time

import django


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daka_web.settings')

    django.setup()

    from daka.tasks import run_daka
    from daka_web.settings import TASK_PERIOD

    while True:
        run_daka()
        time.sleep(TASK_PERIOD)


if __name__ == '__main__':
    main()
