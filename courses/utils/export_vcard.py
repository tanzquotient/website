from io import BytesIO, StringIO

from django.http import HttpResponse
from vobject.vcard import *
from vobject import *

from courses.models import UserProfile
from courses.utils import export_zip, clean_filename


def write_vcard(data, file):
    for user in data:
        card = vCard()
        card.add('n')
        card.n.value = Name(family=user.last_name, given=user.first_name)
        card.add('fn')
        card.fn.value = "{} {}".format(user.first_name, user.last_name)
        card.add("email")
        card.email.value = user.email
        if user.profile.phone_number:
            card.add("tel")
            card.tel.value = user.profile.phone_number
        card.add("gender")
        card.gender.value = 'M' if user.profile.gender == UserProfile.Gender.MEN else 'F'

        file.write(card.serialize())


def export_vcard(title, data, multiple=False):

    if multiple:
        files = dict()
        for count, item in enumerate(data):
            file = StringIO()
            write_vcard(item['data'], file)
            files["{}_{}.vcf".format(count + 1, item['name'])] = file.getvalue()

        return export_zip(title, files)

    else:
        response = HttpResponse(content_type='text/vcard')
        response['Content-Disposition'] = 'attachment; filename="{}.vcf"'.format(clean_filename(title))
        write_vcard(data, response)
        return response