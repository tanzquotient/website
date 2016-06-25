from django.conf import settings
from paramiko.client import SSHClient
import os
import re
import logging
log = logging.getLogger('payment')


class FDSConnection():

    def __init__(self):
        self.client = SSHClient()
        self.client.load_host_keys(settings.FDS_HOST_KEY)
        self.client.connect(settings.FDS_HOST, username=settings.FDS_USER, key_filename=settings.FDS_PRIVATE_KEY, port=settings.FDS_PORT)
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
                #self.sftp.remove(file)
            else:
                log.debug("Skipping already present file: {}".format(file))


import xml.etree.ElementTree as ET
from payment.models import Payment
from datetime import datetime

class ISO2022Parser:

    def __init__(self):
        pass

    def parse(self):
        fds_data_path = os.path.join(settings.BASE_DIR, settings.FDS_DATA_PATH)
        log.debug("parse")
        for file in os.listdir(fds_data_path):
            if ('.xml' in file) and ('processed' not in file):
                filepath = os.path.join(fds_data_path, file)
                self.parse_file(filepath)


    def parse_user_string(self, string):

        prog = re.compile(r"GIRO AUS KONTO (?P<account_nr>[\-0-9]*)\s((?P<name>.*)\s(?P<street>[\S+]*\s[0-9]*)\s(?P<plz>[0-9]{4})\s(?P<city>[\S+]*))\sMITTEILUNGEN: (?P<note>.*)")
        match_obj = prog.match(string)
        if match_obj:
            data = {'account_nr' : match_obj.group('account_nr'),
                    'name' : match_obj.group('name'),
                    'street': match_obj.group('street'),
                    'plz': match_obj.group('plz'),
                    'city': match_obj.group('city'),
                    'note': match_obj.group('note')}
            log.debug(data)

            return data
        else:
            return None


    def parse_file(self, filename):
        log.debug("parse file")

        tree = ET.parse(filename)
        root = tree.getroot()
        payments = []

        ns = {'pf': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.04'}

        def find_or_empty(transaction, name):
            e = transaction.find(".//pf:{}".format(name),ns)
            return e.text if e is not None else ""

        for transaction in root.findall(".//pf:Ntry",ns):
            log.debug("Processing Payment...")

            payment = Payment()

            # for IBAN transactions
            payment.bic = find_or_empty(transaction, 'BICFI')
            payment.iban = find_or_empty(transaction, 'DbtrAcct')

            # unique reference number by postfinance
            payment.transaction_id = find_or_empty(transaction, 'AcctSvcrRef')
            payment.amount = float(find_or_empty(transaction, 'Amt') or 0.0)
            payment.currency_code = transaction.find('.//pf:Amt', ns).get('Ccy')

            # remittance user string
            payment.remittance_user_string = find_or_empty(transaction, 'AddtlNtryInf')

            user_data = self.parse_user_string(payment.remittance_user_string)
            if user_data is not None:
                payment.name = user_data['name']
                payment.address = u"{}, {} {}".format(user_data['street'], user_data['plz'], user_data['city'])
                payment.remittance_user_string = user_data['note']

            payment.state = Payment.State.NEW
            #postal_address = debitor.find(".//pf:PstlAdr",ns)
            #if postal_address:
            #    addresses = debitor.findall(".//pf:AdrLine", ns)
            #    payment.address = ", ".join([adr.text for adr in addresses])
            payment.date = datetime.today() # TODO not exactly elegant
            payment.filename = os.path.split(filename)[-1]
            payments.append(payment)
            log.info('Received payment {}'.format(payment.name))

        for payment in payments:
            payment.save()

        os.rename(filename, filename + '.processed')