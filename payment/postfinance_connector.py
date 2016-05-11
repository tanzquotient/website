from django.conf import settings
import pysftp
import os

import logging
log = logging.getLogger('payment')


class FDSConnection():

    def __init__(self):
        pass

    def get_files(self):
        fds_data_path = os.path.join(settings.BASE_DIR, settings.FDS_DATA_PATH)
        with pysftp.Connection(settings.FDS_HOST, username=settings.FDS_USER, password=settings.FDS_PASSWORD) as sftp:
            sftp.get_r('.', fds_data_path)

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
            if not 'processed' in file:
                filepath = os.path.join(fds_data_path, file)
                self.parse_file(filepath)

    def parse_file(self, filename):
        log.debug("parse file")

        tree = ET.parse(filename)
        root = tree.getroot()
        payments = []

        ns = {'pf': 'http://www.six-interbank-clearing.com/de/pain.001.001.03.ch.02.xsd'}

        def find_or_empty(transaction, name):
            e = transaction.find(".//pf:{}".format(name),ns)
            return e.text if e is not None else ""

        for transaction in root.findall(".//pf:CdtTrfTxInf",ns):
            log.debug("Processing Payment...")
            payment = Payment()
            payment.bic = find_or_empty(transaction, 'BIC')
            payment.name = find_or_empty(transaction, 'Nm')
            payment.iban = find_or_empty(transaction, 'IBAN')
            payment.amount = float(find_or_empty(transaction, 'InstdAmt') or 0.0)
            payment.currency_code = transaction.find('.//pf:InstdAmt', ns).get('Ccy')
            payment.remittance_user_string = find_or_empty(transaction, 'Ustrd')
            payment.state = Payment.State.NEW
            postal_address = transaction.find(".//pf:PstlAdr",ns)
            if postal_address:
                street_name = find_or_empty(postal_address, 'StrtNm')
                street_number = find_or_empty(postal_address, 'BldgNb')
                post_code = find_or_empty(postal_address, 'PstCd')
                city = find_or_empty(postal_address, 'TwnNm')
                country = find_or_empty(postal_address, 'Ctry')
                payment.address = "{0} {1}, {2} {3}, {4}".format(street_name, street_number, post_code, city, country)
            payment.date = datetime.today() # TODO not exactly elegant
            payment.filename = os.path.split(filename)[-1]
            payments.append(payment)
            log.info('Received payment by {}'.format(payment.name))

        for payment in payments:
            payment.save()

        os.rename(filename, filename + '.processed')