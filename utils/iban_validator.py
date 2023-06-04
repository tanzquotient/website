from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import string
from itertools import chain


# Method found here: https://codereview.stackexchange.com/questions/135366/python-iban-validation#:~:text=Validating%20the%20IBAN,-Description%20(from%20wiki&text=An%20IBAN%20is%20validated%20by,correct%20as%20per%20the%20country.
def validate_iban(iban):
    _LETTERS = chain(
        enumerate(string.digits + string.ascii_uppercase),
        enumerate(string.ascii_lowercase, 10),
    )
    LETTERS = {ord(d): str(i) for i, d in _LETTERS}

    def _number_iban(iban):
        return (iban[4:] + iban[:4]).translate(LETTERS)

    def generate_iban_check_digits(iban):
        number_iban = _number_iban(iban[:2] + "00" + iban[4:])
        return "{:0>2}".format(98 - (int(number_iban) % 97))

    def valid_iban(iban):
        return int(_number_iban(iban)) % 97 == 1

    iban = iban.replace(" ", "")
    if not (generate_iban_check_digits(iban) == iban[2:4] and valid_iban(iban)):
        raise ValidationError(_("The IBAN is invalid."), code="invalid_iban")
