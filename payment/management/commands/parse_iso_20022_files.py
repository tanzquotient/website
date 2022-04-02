import logging

from django.core.management.base import BaseCommand

from payment.parser.iso_2022_parser import ISO2022Parser

log = logging.getLogger('tq')


class Command(BaseCommand):
    help = '(re)parse ISO 20022 files, ignoring duplicates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='dry run',
        )
        parser.add_argument(
            '--reparse',
            action='store_true',
            dest='reparse',
            default=False,
            help='parse file also if already processed',
        )

    def handle(self, *args, **options):
        log.info('run management command: {}'.format(__file__))
        count = ISO2022Parser.parse_files_and_save_payments(reparse=options['reparse'], dry_run=options['dry_run'])
        log.info('found and parsed {} new transactions'.format(count))
