import re
import unicodedata
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from courses import models as models


def update_user(user: User, user_data: dict) -> User:
    if 'email' in user_data:
        user.email = user_data['email']
    if 'first_name' in user_data:
        user.first_name = user_data['first_name']
    if 'last_name' in user_data:
        user.last_name = user_data['last_name']
    user.save()

    profile = get_or_create_userprofile(user)

    # convenience method. if key is not given, assume same as attr
    def set_if_given(attr: str, key: str = None) -> None:
        if not key:
            key = attr
        if key in user_data:
            setattr(profile, attr, user_data[key])

    set_if_given('legi')
    set_if_given('gender')
    set_if_given('phone_number')
    set_if_given('student_status')
    set_if_given('body_height')
    set_if_given('newsletter')
    set_if_given('get_involved')

    if not user_data["picture"]:
        profile.picture = None
    else:
        name = user_data['picture'].name
        user_data['picture'].name = "{}.{}".format(uuid.uuid4(), name.split(".")[-1])
        set_if_given('picture')
    set_if_given('about_me')

    set_if_given('birthdate')
    set_if_given('nationality')
    set_if_given('residence_permit')
    set_if_given('ahv_number')

    if all((user_data.get(key)) for key in ['street', 'plz', 'city']):
        if profile.address:
            profile.address.street = user_data['street']
            profile.address.plz = user_data['plz']
            profile.address.city = user_data['city']
            profile.address.save()
        else:
            profile.address = models.Address.objects.create_from_user_data(user_data)

    if all((key in user_data) for key in ['iban']):
        if profile.bank_account:
            profile.bank_account.iban = user_data['iban']
            profile.bank_account.bank_name = user_data['bank_name']
            profile.bank_account.bank_zip_code = user_data['bank_zip_code']
            profile.bank_account.bank_city = user_data['bank_city']
            profile.bank_account.bank_country = user_data['bank_country']
            profile.bank_account.save()
        else:
            profile.bank_account = models.BankAccount.objects.create_from_user_data(user_data)

    profile.save()

    return user


def find_unused_username_variant(name, ignore=None):
    un = name
    i = 1
    while User.objects.exclude(username=ignore).filter(username=un).count() > 0:
        un = name + str(i)
        i += 1
    return un


def clean_username(name):
    '''first try to find ascii similar character, then strip away disallowed characters still left'''
    name = unicodedata.normalize('NFKD', name)
    return re.sub('[^0-9a-zA-Z+-.@_]+', '', name)


def get_or_create_userprofile(user):
    try:
        return models.UserProfile.objects.get(user=user)
    except ObjectDoesNotExist:
        userprofile = models.UserProfile(user=user)
        return userprofile