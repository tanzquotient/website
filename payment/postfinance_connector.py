import logging
import os
import re

from django.conf import settings
from django.db import DatabaseError
from paramiko.client import SSHClient

log = logging.getLogger('payment')


class FDSConnection():
    def __init__(self):
        self.client = SSHClient()
        self.client.load_host_keys(settings.FDS_HOST_KEY)
        self.client.connect(settings.FDS_HOST, username=settings.FDS_USER, key_filename=settings.FDS_PRIVATE_KEY,
                            port=settings.FDS_PORT)
        self.sftp = self.client.open_sftp()
        log.info("Connected to FDS")

    def get_files(self):
        log.info("Receiving files from FDS...")
        fds_data_path = os.path.join(settings.BASE_DIR, settings.FDS_DATA_PATH)

        local_files = os.listdir(fds_data_path)

        self.sftp.chdir('yellow-net-reports')
        for file in self.sftp.listdir():
            if file not in local_files and file + '.processed' not in local_files:
                log.info("Receiving {}".format(file))
                self.sftp.get(file, os.path.join(fds_data_path, file))
                # self.sftp.remove(file)
            else:
                log.debug("Skipping already present file: {}".format(file))


import xml.etree.ElementTree as ET
from payment.models import Payment
from datetime import datetime


def find_fds_files(processed=False):
    fds_data_path = os.path.join(settings.BASE_DIR, settings.FDS_DATA_PATH)
    log.debug("find fds files under '{}'".format(fds_data_path))
    for file in os.listdir(fds_data_path):
        if ('.xml' in file) and (('processed' in file) == processed):
            yield os.path.join(fds_data_path, file)


class ISO2022Parser:
    @staticmethod
    def parse(reparse=False, dry_run=False):
        for filename in find_fds_files(processed=reparse):
            payments = ISO2022Parser.parse_file(filename)
            if not dry_run:
                ISO2022Parser.save_payments(filename, payments)

    @staticmethod
    def parse_user_string(string):
        data = {'account_nr': "",
                'name': "",
                'street': "",
                'plz': "",
                'city': "",
                'note': string}

        postfinance_regex = re.compile(
            r"GIRO AUS KONTO (?P<account_nr>[\-0-9]*)\s((?P<name>.*)\s(?P<street>[\S+]*\s[0-9]*)\s(?P<plz>[0-9]{4})\s(?P<city>[\S+]*))\sMITTEILUNGEN:(?P<note>.*)")
        postfinance_matches = postfinance_regex.search(string)
        if postfinance_matches:
            data['account_nr'] = postfinance_matches.group('account_nr')
            data['name'] = postfinance_matches.group('name')
            data['street'] = postfinance_matches.group('street')
            data['plz'] = postfinance_matches.group('plz')
            data['city'] = postfinance_matches.group('city')
            data['note'] = postfinance_matches.group('note')

        absender_matches = re.compile(r"ABSENDER:\s((?P<name>.*)\s(?P<plz>[0-9]{4})\s(?P<city>[\S+]*))").search(string)
        if absender_matches:
            data['name'] = absender_matches.group('name')
            data['plz'] = absender_matches.group('plz')
            data['city'] = absender_matches.group('city')

        auftraggeber_regex = re.compile(
            r"AUFTRAGGEBER:\s((?P<name>.*)\s(?P<street>[\S+]*\s[0-9]*)\s(?P<plz>[0-9]{4})\s(?P<city>[\S+]*))")
        auftraggeber_matches = auftraggeber_regex.search(string)
        if auftraggeber_matches:
            data['name'] = auftraggeber_matches.group('name')
            data['street'] = auftraggeber_matches.group('street')
            data['plz'] = auftraggeber_matches.group('plz')
            data['city'] = auftraggeber_matches.group('city')

        mitteilungen_matches = re.compile(r"MITTEILUNGEN:(?P<note>.*)").search(string)
        if mitteilungen_matches:
            data['note'] = mitteilungen_matches.group('note')

        return data

    @staticmethod
    def parse_file(filename):
        log.info("parse file {}".format(filename))

        tree = ET.parse(filename)
        root = tree.getroot()
        payments = []

        ns = {'pf': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.04'}

        def find_or_empty(transaction, name):
            e = transaction.find(".//pf:{}".format(name), ns)
            return e.text if e is not None else ""

        for transaction in root.findall(".//pf:Ntry", ns):
            # check if transaction id is valid transaction exists already -> skip
            transaction_id = find_or_empty(transaction, 'AcctSvcrRef')
            only_zero_regex = re.compile(r"0*")
            if only_zero_regex.match(transaction_id):
                log.warning("A transaction of file {} has an invalid transaction ID: {}".format(filename, transaction_id))
                continue
            log.info("processing transaction {}".format(transaction_id))
            payments_count = Payment.objects.filter(transaction_id=transaction_id).count()
            if payments_count > 0:
                log.warning(
                    "transaction {} in file {} already exists in database".format(transaction_id, filename))
                continue

            payment = Payment()

            # for IBAN transactions
            payment.bic = find_or_empty(transaction, 'BICFI')
            payment.iban = find_or_empty(transaction, 'DbtrAcct')

            # unique reference number by postfinance
            payment.transaction_id = transaction_id
            payment.amount = float(find_or_empty(transaction, 'Amt') or 0.0)
            payment.currency_code = transaction.find('.//pf:Amt', ns).get('Ccy')

            # Credit or Debit
            credit_debit = find_or_empty(transaction, 'CdtDbtInd')
            if credit_debit == 'CRDT':
                payment.credit_debit = Payment.CreditDebit.CREDIT
            elif credit_debit == 'DBIT':
                payment.credit_debit = Payment.CreditDebit.DEBIT
            else:
                payment.credit_debit = Payment.CreditDebit.UNKNOWN

            # remittance user string
            payment.remittance_user_string = find_or_empty(transaction, 'AddtlNtryInf')

            user_data = ISO2022Parser.parse_user_string(payment.remittance_user_string)
            if user_data is not None:
                payment.name = user_data['name']
                payment.address = "{}, {} {}".format(user_data['street'], user_data['plz'], user_data['city'])
                payment.remittance_user_string = user_data['note']

            payment.state = Payment.State.NEW
            # postal_address = debitor.find(".//pf:PstlAdr",ns)
            # if postal_address:
            #    addresses = debitor.findall(".//pf:AdrLine", ns)
            #    payment.address = ", ".join([adr.text for adr in addresses])
            payment.date = datetime.today()  # TODO not exactly elegant
            payment.filename = os.path.split(filename)[-1]
            payments.append(payment)
            log.info('Detected payment: {}'.format(payment))

        return payments

    @staticmethod
    def save_payments(filename, payments):
        for payment in payments:
            try:
                payment.save()
            except DatabaseError as e:
                log.error(str(e))

        # even if there was an error, we rename the file to ensure it is not again and again reprocessed,
        # throwing errors
        os.rename(filename, filename + '.processed')
