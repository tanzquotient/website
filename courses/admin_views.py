from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.forms.extras.widgets import SelectDateWidget

from django.utils.translation import ugettext as _

import datetime

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from courses.models import *

from . import services

class VoucherGenerationForm(forms.Form):
    amount = forms.IntegerField(label=_("Choose amount"), initial=20)
    purpose = forms.ModelChoiceField(queryset=VoucherPurpose.objects)
    expires_flag = forms.BooleanField(label=_("Set expire date?"), initial=False, required=False)
    expires = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today() + datetime.timedelta(days=365 * 2))


@staff_member_required
def voucher_generation_view(request):
    form = None

    if 'generate' in request.POST:
        form = VoucherGenerationForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            purpose = form.cleaned_data['purpose']
            expires_flag = form.cleaned_data['expires_flag']
            expires = form.cleaned_data['expires']

            # generate amount many vouchers
            for i in range(0, amount):
                v = Voucher(purpose=purpose, expires=expires if expires_flag else None)
                v.save()

            return HttpResponseRedirect(reverse('admin:courses_voucher_changelist'))

    if not form:
        form = VoucherGenerationForm()

    return render(request, 'courses/auth/action_voucher_generation.html', {
        'form': form,
    })