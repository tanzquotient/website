from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from courses.forms import VoucherGenerationForm
from courses.models import *


@staff_member_required
def voucher_generation_view(request):
    form = None

    if 'generate' in request.POST:
        form = VoucherGenerationForm(request.POST)

        if form.is_valid():
            number_of_vouchers = form.cleaned_data['number_of_vouchers']
            percentage = form.cleaned_data['percentage']
            purpose = form.cleaned_data['purpose']
            expires_flag = form.cleaned_data['expires_flag']
            expires = form.cleaned_data['expires']

            for i in range(0, number_of_vouchers):
                v = Voucher(purpose=purpose, percentage=percentage, expires=expires if expires_flag else None)
                v.save()

            return HttpResponseRedirect(reverse('admin:courses_voucher_changelist'))

    if not form:
        form = VoucherGenerationForm()

    return render(request, 'courses/auth/action_voucher_generation.html', {
        'form': form,
    })