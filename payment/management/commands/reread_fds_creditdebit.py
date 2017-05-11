from django.core.management.base import BaseCommand

from payment.models import *
from courses.models import *
from payment.postfinance_connector import find_fds_files

import logging

log = logging.getLogger('tq')

import xml.etree.ElementTree as ET
from payment.models import Payment
from datetime import datetime


def _reparse_file(filename):
    log.debug("parse processed file again")

    tree = ET.parse(filename)
    root = tree.getroot()

    ns = {'pf': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.04'}

    def find_or_empty(transaction, name):
        e = transaction.find(".//pf:{}".format(name), ns)
        return e.text if e is not None else ""

    fixed = unfixed = 0

    for transaction in root.findall(".//pf:Ntry", ns):
        log.debug("see transaction {}".format(transaction))
        transaction_id = find_or_empty(transaction, 'AcctSvcrRef')

        payments = Payment.objects.filter(transaction_id=transaction_id).all()
        if len(payments) != 1:
            log.warning("multiple or no payments found for transaction {} in file {}".format(transaction_id, filename))
            unfixed += 1
            continue

        payment = payments[0]

        # Credit or Debit
        credit_debit = find_or_empty(transaction, 'CdtDbtInd')
        if credit_debit == 'CRDT':
            payment.credit_debit = Payment.CreditDebit.CREDIT
        elif credit_debit == 'DBIT':
            payment.credit_debit = Payment.CreditDebit.DEBIT
        else:
            payment.credit_debit = Payment.CreditDebit.UNKNOWN

        payment.save()
        fixed += 1

    return fixed, unfixed


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info('run management command: {}'.format(__file__))
        log.info(
            'the following fds transactions have are reread:')
        fixed = unfixed = 0
        for filepath in find_fds_files(processed=True):
            f, u = _reparse_file(filepath)
            fixed += f
            unfixed += u
            log.info("{}".format(filepath))
        log.info('TOTAL fixed: {}, unfixed: {}'.format(fixed, unfixed))
