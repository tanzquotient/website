from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView, FormMixin

from courses.models import Offering, Subscribe, SubscribeState, PaymentMethod
from payment.services import remind_of_payment


class OfferingFinanceUnpaidView(
    PermissionRequiredMixin, TemplateView, ProcessFormView, FormMixin
):
    template_name = "finance/offering/unpaid/index.html"
    permission_required = "payment.change_payment"
    form_class = forms.Form

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context["active"] = "unpaid"
        context["offering"] = get_object_or_404(Offering, id=kwargs["offering"])
        subscriptions = list(
            Subscribe.objects.filter(
                course__offering_id=kwargs["offering"], state=SubscribeState.CONFIRMED
            )
            .select_related("user", "user__profile", "course", "course__offering")
            .prefetch_related("payment_reminders")
            .order_by("user__first_name")
            .all()
        )
        context["subscriptions"] = subscriptions
        context["count"] = len(subscriptions)
        context["users_count"] = len(
            {subscription.user_id for subscription in subscriptions}
        )
        context["courses_count"] = len(
            {subscription.course_id for subscription in subscriptions}
        )
        context["open_total"] = sum(
            [subscription.open_amount() for subscription in subscriptions]
        )
        return context

    def post(self, request, **kwargs):
        self.success_url = reverse("payment:offering_unpaid", kwargs=kwargs)

        if "remind" in request.POST:
            remind = request.POST["remind"]
            if remind == "all":
                for subscription in Subscribe.objects.filter(
                    course__offering_id=kwargs["offering"],
                    state=SubscribeState.CONFIRMED,
                ):
                    remind_of_payment(subscription)
            else:
                subscription = Subscribe.objects.get(id=remind)
                remind_of_payment(subscription)

        if "mark_as_paid" in request.POST:
            subscription: Subscribe = Subscribe.objects.get(
                id=request.POST["mark_as_paid"]
            )
            subscription.mark_as_paid(PaymentMethod.MANUAL, request.user)

        return super().post(request)
