import reversion
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import render
from django.urls import reverse

from courses.forms import VoucherGenerationForm
from courses.models import *


@staff_member_required
def voucher_generation_view(request: HttpRequest) -> HttpResponse:
    form = None

    if "generate" in request.POST:
        form = VoucherGenerationForm(request.POST)

        if form.is_valid():
            number_of_vouchers = form.cleaned_data["number_of_vouchers"]
            percentage = form.cleaned_data.get("percentage")
            amount = form.cleaned_data.get("amount")
            purpose = form.cleaned_data["purpose"]
            expires_flag = form.cleaned_data["expires_flag"]
            expires = form.cleaned_data["expires"]

            for _ in range(0, number_of_vouchers):
                with reversion.create_revision():
                    Voucher.objects.create(
                        purpose=purpose,
                        amount=amount,
                        percentage=percentage,
                        expires=expires if expires_flag else None,
                    )
                    if request.user:
                        reversion.set_user(request.user)
                        reversion.set_comment(
                            f"{request.user.get_full_name()} created "
                            f"{number_of_vouchers} vouchers"
                        )

            return HttpResponseRedirect(reverse("admin:courses_voucher_changelist"))

    if not form:
        form = VoucherGenerationForm()

    return render(
        request, "courses/auth/action_voucher_generation.html", {"form": form}
    )
