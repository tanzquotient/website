import csv
import datetime
import logging

from django.core.management.base import BaseCommand

from payment.models import *
from payment.parser.iso_2022_parser import ISO2022Parser

log = logging.getLogger('tq')


class Command(BaseCommand):
    help = 'Imports a manually exported csv file from the PostFinance backend'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):

        with open(options['filename'], "r", encoding='ISO-8859-1') as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            # remove header and footer
            data = list(reader)[7:-3]

        transactions = [(datetime.datetime.strptime(tr[0], "%Y-%m-%d"),
                         ISO2022Parser.parse_user_string(tr[1]),
                         tr[2]) for tr in data]

        for date, transaction, amount in transactions:
            pay = Payment()

            pay.date = date
            pay.name = transaction["name"]
            pay.address = transaction["street"] + ", " + transaction["city"]
            pay.remittance_user_string = transaction["note"]
            pay.credit_debit = "credit"
            try:
                pay.amount = float(amount)
                pay.save()
            except:
                print("Could not convert {} to float".format(amount))
