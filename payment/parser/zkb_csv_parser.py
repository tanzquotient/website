import codecs
import csv
from datetime import datetime
from decimal import Decimal
from io import StringIO

from payment.models import Payment, FinanceFile
from payment.models.choices import FinanceFileType, CreditDebit


class ZkbCsvParser:

    @staticmethod
    def parse_files_and_save_payments() -> list[Payment]:

        payments: list[Payment] = []
        new_files = FinanceFile.objects.filter(type=FinanceFileType.ZKB_CSV, processed=False).all()
        for file in new_files:
            payments += ZkbCsvParser.parse_file(file)

        return payments

    @staticmethod
    def parse_file(finance_file: FinanceFile) -> list[Payment]:
        csv_file = finance_file.file

        csv_file.open()
        content = StringIO(codecs.decode(csv_file.read(), 'utf-8-sig'))
        csv_file.close()

        reader = csv.DictReader(content, delimiter=";")

        payments = []

        for row in reader:
            payment = Payment()
            payment.file = finance_file
            payment.filename = csv_file.name
            payment.date = datetime.strptime(row['Datum'], "%d.%m.%Y")
            payment.transaction_id = row['ZKB-Referenz']
            payment.currency_code = 'CHF'
            payment.remittance_user_string = row['Zahlungszweck']
            payment.comment = row['Buchungstext']

            # Parse name and address from details
            details: str = row['Details']
            parts = details.split(',')
            payment.name = parts[0] if len(parts) > 0 else ''
            payment.address = ','.join(parts[1:]) if len(parts) > 1 else ''

            # Read amount from corresponding fields
            if row['Gutschrift CHF']:
                payment.credit_debit = CreditDebit.CREDIT
                payment.amount = Decimal(row['Gutschrift CHF'])
            else:
                payment.credit_debit = CreditDebit.DEBIT
                payment.amount = Decimal(row['Belastung CHF'])

            # Save payment only if it has not been saved before
            if not Payment.objects.filter(transaction_id=payment.transaction_id).exists():
                payment.save()
                payments.append(payment)

        finance_file.processed = True
        finance_file.save()

        return payments
