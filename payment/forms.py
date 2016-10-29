from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from courses.models import Subscribe, Voucher, Course, Teach
from django.contrib.auth.models import User

import datetime
from django.utils.translation import ugettext as _
import re

RE_USI = r"([USIusi]{0,3}-)?(?P<usi>[a-zA-Z0-9]{6,6})"
PROG_USI = re.compile(RE_USI)


def validate_usi_exists(raw_usi):
    """
    Validates if the specified USI is a valid USI
    :param value: the usi to be validated
    :return:
    """
    matches = PROG_USI.match(raw_usi)
    if Subscribe.objects.filter(usi=matches.group('usi')).count() == 0:
        raise ValidationError(_('The specified USI does not exist'))


def voucher_valid(code):
    """
    Validates if a voucher is valid
    :param code: the voucher key to be validated
    :return:
    """
    if not Voucher.objects.filter(key=code).count() > 0:
        raise ValidationError(_('The specified voucher code does not exist'))
    voucher = Voucher.objects.filter(key=code).first()
    if voucher.used:
        raise ValidationError(_('The specified voucher code has already been used'))
    if voucher.expires:
        if not voucher.expires >= datetime.datetime.today().date():
            raise ValidationError(_('The specified voucher code is expired'))


class USIForm(forms.Form):
    usi_validator = RegexValidator(regex=RE_USI, message=_("Please enter a valid USI"))
    usi = forms.CharField(max_length=10, label=_("Unique Course Identifier (USI)"),
                          validators=[usi_validator, validate_usi_exists, ])

    def clean_usi(self):
        data = self.cleaned_data['usi']
        match = PROG_USI.match(data)
        return match.group('usi')


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
        courses = list(courses)
        courses.sort(
            key=lambda
                course: course.get_period().date_from if course.get_period() and course.get_period().date_from else datetime.date(
                year=1990, month=
                1, day=1), reverse=True)
        super(CourseForm, self).__init__(*args, **kwargs)
        self.fields['course'] = forms.ChoiceField(label=_("Select Course"),
                                                  choices=[(course.id, course) for course in courses])
