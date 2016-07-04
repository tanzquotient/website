from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from courses.models import Subscribe, Voucher, Course, Teach
from django.contrib.auth.models import User

import datetime
from django.utils.translation import ugettext as _


def validate_usi_exists(value):
    """
    Validates if the specified USI is a valid USI
    :param value: the usi to be validated
    :return:
    """
    if Subscribe.objects.filter(usi=value.strip('#')).count() == 0:
        raise ValidationError(_('The specified USI does not exist'))


def voucher_valid(value):
    """
    Validates if a voucher is valid
    :param value: the voucher key to be validated
    :return:
    """
    if not Voucher.objects.filter(key=value).count() > 0:
        raise ValidationError(_('The specified voucher code does not exist'))
    voucher = Voucher.objects.filter(key=value).first()
    if not voucher.used == False:
        raise ValidationError(_('The specified voucher code has already been used'))
    if voucher.expires:
        if not voucher.expires >= datetime.datetime.today().date():
            raise ValidationError(_('The specified voucher code is expired'))


class USIForm(forms.Form):
    usi_validator = RegexValidator(regex='#?[a-zA-Z0-9]{6}', message=_("Please enter a valid USI"))
    usi = forms.CharField(max_length=7, label=_("Unique Course Identifier (USI)"),
                          validators=[usi_validator, validate_usi_exists, ])


class VoucherForm(forms.Form):
    voucher_code = forms.CharField(max_length=6, label=_("Voucher Code"), validators=[voucher_valid, ])

class CourseForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        courses = []
        if user is not None:
            # if the user is a superuser we show him all courses, otherwise only the courses he teaches
            if user.is_superuser:
                courses = Course.objects.all()
            else:
                courses = [teach.course for teach in Teach.objects.filter(teacher=user).all()]
        super(CourseForm, self).__init__(*args, **kwargs)
        self.fields['course'] = forms.ChoiceField(label=_("Select Course"), choices=[(course.id, course) for course in courses])

