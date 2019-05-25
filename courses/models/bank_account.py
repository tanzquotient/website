from django.db import models
from django_countries.fields import CountryField

from courses import managers


class BankAccount(models.Model):
    iban = models.CharField(max_length=255)
    iban.help_text = "IBAN in the standardized format."
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_name.help_text = "Name of the bank."
    bank_zip_code = models.CharField(max_length=255, blank=True, null=True)
    bank_zip_code.help_text = "Zipcode of the bank."
    bank_city = models.CharField(max_length=255, blank=True, null=True)
    bank_city.help_text = "City of the bank."
    bank_country = CountryField(default='CH', blank=True, null=True)

    objects = managers.BankAccountManager()

    def __str__(self):
        return "{} ({})".format(self.iban, self.bank_info_str())

    def bank_info_str(self):
        return "{}, {} {}, {}".format(self.bank_name, self.bank_zip_code, self.bank_city, self.bank_country)
