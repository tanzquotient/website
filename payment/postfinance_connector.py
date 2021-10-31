import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from io import StringIO

from django.core.files.base import ContentFile
from django.db import DatabaseError
from paramiko import RSAKey
from paramiko.client import SSHClient, AutoAddPolicy

from payment.models import Payment, PostfinanceFile
from payment.models.choices import CreditDebit, State
from tq_website.settings import FDS_PORT, FDS_HOST, FDS_PRIVATE_KEY, FDS_USER

log = logging.getLogger('payment')


class FDSConnection:
    def __init__(self):
        private_key = RSAKey.from_private_key(StringIO(FDS_PRIVATE_KEY))
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(FDS_HOST, username=FDS_USER, pkey=private_key, port=FDS_PORT)
        self.sftp = self.client.open_sftp()
        log.info("Connected to FDS")

    def get_files(self):
        log.info("Receiving files from FDS...")

        # Iterate over all remote files
        self.sftp.chdir('yellow-net-reports')
        filenames = self.sftp.listdir()
        log.info("Found {} files on server".format(filenames))
        for filename in filenames:
            if not PostfinanceFile.objects.filter(name=filename).exists():
                log.info("Receiving {}".format(filename))
                with self.sftp.open(filename) as file:
                    content = file.read()
                if isinstance(content, str):
                    content = content.encode('utf-8')
                content_file = ContentFile(content)
                db_file = PostfinanceFile.objects.create(name=filename, downloaded_at=datetime.now())
                db_file.file.save(filename, content_file)
                log.info("Saved {}".format(filename))
            else:
                log.info("Skipping already existing file: {}".format(filename))




def find_fds_files(include_processed=False):
    if include_processed:
        return PostfinanceFile.objects
    return PostfinanceFile.objects.filter(processed=False).all()



class ISO2022Parser:
    @staticmethod
    def parse(reparse=False, dry_run=False):
        count = 0
        for file in find_fds_files(include_processed=reparse):
            payments = ISO2022Parser.parse_file(file)
            count += len(payments)
            if not dry_run:
                ISO2022Parser.save_payments(payments)
                file.processed = True
                file.save()
        return count

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
    def parse_file(db_file):
        filename = db_file.name
        log.info("parse file {}".format(filename))
        if db_file.processed:
            log.info("file has already been processed previously")

        tree = ET.parse(db_file.file)
        root = tree.getroot()
        payments = []

        ns = {'pf': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.04'}

        def find_or_empty(transaction, name):
            e = transaction.find(".//pf:{}".format(name), ns)
            return e.text if e is not None else ""

        for transaction in root.findall(".//pf:Ntry", ns):
            # check if transaction id is valid transaction exists already -> skip
            transaction_id = find_or_empty(transaction, 'AcctSvcrRef')
            only_zero_regex = re.compile(r"^0*$")
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
                payment.credit_debit = CreditDebit.CREDIT
            elif credit_debit == 'DBIT':
                payment.credit_debit = CreditDebit.DEBIT
            else:
                payment.credit_debit = CreditDebit.UNKNOWN

            # remittance user string
            payment.remittance_user_string = find_or_empty(transaction, 'AddtlNtryInf')

            user_data = ISO2022Parser.parse_user_string(payment.remittance_user_string)
            if user_data is not None:
                payment.name = user_data['name']
                payment.address = "{}, {} {}".format(user_data['street'], user_data['plz'], user_data['city'])
                payment.remittance_user_string = user_data['note']

            payment.state = State.NEW
            # postal_address = debitor.find(".//pf:PstlAdr",ns)
            # if postal_address:
            #    addresses = debitor.findall(".//pf:AdrLine", ns)
            #    payment.address = ", ".join([adr.text for adr in addresses])
            payment.date = datetime.today()  # TODO not exactly elegant
            payment.filename = filename
            payment.file = db_file
            payments.append(payment)
            log.info('Detected payment: {}'.format(payment))

        return payments

    @staticmethod
    def save_payments(payments):
        for payment in payments:
            try:
                payment.save()
            except DatabaseError as e:
                log.error(str(e))
