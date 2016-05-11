from django.conf import settings
import pysftp
import os

class FDSConnection():

    def __init__(self):
        pass

    def get_files(self):
        fds_data_path = os.path.join(settings.BASE_DIR, settings.FDS_DATA_PATH)
        with pysftp.Connection(settings.FDS_HOST, username=settings.FDS_USER, password=settings.FDS_PASSWORD) as sftp:
            sftp.get_r('', fds_data_path)

import xml.etree.ElementTree as ET
from payment.models import Payment
from datetime import datetime

class ISO2022Parser:

    def __init__(self):
        pass

    def parse(self):
        fds_data_path = os.path.join(settings.BASE_DIR, settings.FDS_DATA_PATH)

        for file in os.listdir(fds_data_path):
            if not 'processed' in file:
                filepath = os.path.join(fds_data_path, file)
                self.parse_file(filepath)

    def parse_file(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        payments = []
        for transaction in root.findall('CdtTrfTxInf'):
            payment = Payment()
            payment.bic = transaction.find('BIC').text
            payment.name = transaction.find('Nm').text
            payment.iban = transaction.find('IBAN').text
            payment.amount = float(transaction.find('InstdAmt').text)
            payment.currency_code = transaction.find('InstdAmt').get('Ccy')
            postal_address = transaction.find('PstlAdr')
            street_name = postal_address.find('StrtNm').text
            street_number = postal_address.find('BldgNb').text
            post_code = postal_address.find('PstCd').text
            city = postal_address.find('TwnNm').text
            country = postal_address.find('Ctry').text
            payment.address = "{0} {1}, {2} {3}, {4}".format(street_name, street_number, post_code, city, country)
            payment.date = datetime.strptime(root.find('ReqdExctnDt').text, "%Y-%m-%d")
            payments.append(payment)

        for payment in payments:
            payment.save()

        os.rename(filename, filename + '.processed')