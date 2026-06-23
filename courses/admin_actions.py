import shutil
import tempfile
import zipfile

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from reversion import revisions as reversion

import courses.services.matching.change_matching
import courses.services.matching.do_matching
import courses.services.matching.switch_out
from courses.models import *
from email_system.services import send_email
from tq_website import settings

from . import services
from .admin_forms import (
    CopyCourseForm,
    EmailListForm,
    MoveToWaitingListForm,
    RejectForm,
    SendCourseEmailForm,
    SwitchOutForm,
)
from .emailcenter import create_course_info
from .forms import CreateSendVoucherForm, DownloadVouchersForm, SendVoucherEmailForm


@admin.action(description="Set displayed")
def display(modeladmin, request, queryset):
    queryset.update(display=True)


@admin.action(description="Set undisplayed")
def undisplay(modeladmin, request, queryset):
    queryset.update(display=False)


@admin.action(description="Activate")
def activate(modeladmin, request, queryset):
    queryset.update(active=True)


@admin.action(description="Deactivate")
def deactivate(modeladmin, request, queryset):
    queryset.update(active=False)


@admin.action(description="Enable early sign-up")
def enable_early_signup(modeladmin, request, queryset):
    # need to loop in order to call custom save() method
    skipped = 0
    for instance in queryset:
        if not instance.type.predecessors.exists():
            skipped += 1
            continue
        instance.early_signup = True
        instance.save()
    if skipped:
        messages.warning(
            request,
            f"{skipped} course(s) skipped: their course type has no predecessors configured.",
        )


@admin.action(description="Disable early sign-up")
def disable_early_signup(modeladmin, request, queryset):
    queryset.update(early_signup=False)


@admin.action(description="Cancel course. This rejects all participants.")
def cancel(modeladmin, request, queryset: QuerySet[Course]) -> None:
    for c in queryset.all():
        services.subscriptions.reject_subscriptions(
            c.subscriptions.active(), RejectionReason.COURSE_CANCELLED
        )
        c.cancelled = True
        c.active = False
        c.display = False
        c.save()
        for teacher in c.get_teachers():
            send_email(
                to=teacher.email,
                reply_to=settings.EMAIL_ADDRESS_DANCE_ADMIN,
                template="teacher_course_cancelled",
                context=dict(
                    first_name=teacher.first_name,
                    last_name=teacher.last_name,
                    course=c.type.title,
                    course_info=create_course_info(c),
                ),
            )


@admin.action(description="Create copy of courses in another offering")
def copy_courses(modeladmin, request, queryset):
    form = None

    if "copy" in request.POST:
        form = CopyCourseForm(request.POST)

        if form.is_valid():
            offering = form.cleaned_data["offering"]

            for c in queryset:
                services.courses.copy_course(
                    c,
                    to=offering,
                )

            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = CopyCourseForm(
            initial={
                "_selected_action": map(str, queryset.values_list("id", flat=True)),
                "offering": services.get_subsequent_offering(),
            }
        )

    return render(
        request,
        "courses/auth/action_copy_course.html",
        {
            "courses": queryset,
            "copy_form": form,
        },
    )


@admin.action(description="Confirm selected subscriptions")
def confirm_subscriptions(modeladmin, request, queryset):
    # manually send confirmation mails
    services.subscriptions.confirm_subscriptions(queryset, request)


@admin.action(
    description="Confirm selected subscriptions (allow singles in couple courses)"
)
def confirm_subscriptions_allow_singles(modeladmin, request, queryset):
    # manually send confirmation mails
    services.subscriptions.confirm_subscriptions(queryset, request, True)


@admin.action(description="Unconfirm subscriptions (be sure to reconfirm them later!)")
def unconfirm_subscriptions(modeladmin, request, queryset):
    # manually send confirmation mails
    services.subscriptions.unconfirm_subscriptions(queryset, request)


@admin.action(description="Reject selected subscriptions")
def reject_subscriptions(self, request, queryset):
    form = None

    if "reject" in request.POST:
        form = RejectForm(request.POST)

        if form.is_valid():
            reason = form.cleaned_data["reason"]

            services.subscriptions.reject_subscriptions(
                queryset, reason, form.cleaned_data["send_email"]
            )

            return HttpResponseRedirect(request.get_full_path())

    if not form:
        selected_action = map(str, queryset.values_list("id", flat=True))
        form = RejectForm(
            initial={"_selected_action": selected_action, "send_email": True}
        )

    return render(
        request,
        "courses/auth/action_reject.html",
        {
            "subscriptions": queryset,
            "reason_form": form,
        },
    )


@admin.action(description="Unreject subscriptions")
def unreject_subscriptions(modeladmin, request, queryset):
    # manually send confirmation mails
    services.subscriptions.unreject_subscriptions(queryset, request)


@admin.action(description="Match partners (chronologically, body height optimal)")
def match_partners(modeladmin, request, queryset):
    services.match_partners(queryset, request)


@admin.action(
    description="Unmatch partners (both partners must be selected and unconfirmed)"
)
def unmatch_partners(modeladmin, request, queryset):
    courses.services.matching.change_matching.unmatch_partners(queryset, request)


@admin.action(
    description="Break up (unmatch) couple (both couple partners must be selected and unconfirmed)"
)
def breakup_couple(modeladmin, request, queryset):
    courses.services.matching.change_matching.breakup_couple(queryset, request)


@admin.action(
    description="Correct matching_state to COUPLE (both partners must be matched together, can already be confirmed)"
)
def correct_matching_state_to_couple(modeladmin, request, queryset):
    courses.services.matching.change_matching.correct_matching_state_to_couple(
        queryset, request
    )


@admin.action(description="Switch out partners (select 2 users to switch)")
def switch_out_partner(modeladmin, request, queryset):
    if queryset.count() != 2:
        messages.error(
            request,
            "Select exactly 2 subscriptions: one confirmed+matched and one new/waiting+unmatched.",
        )
        return

    confirmed_sub = None
    new_sub = None
    for s in queryset.select_related("course", "course__type"):
        if (
            s.state
            in (
                SubscribeState.NEW,
                SubscribeState.CONFIRMED,
                SubscribeState.PAID,
            )
            and s.matching_state in MatchingState.MATCHED_STATES
        ):
            confirmed_sub = s
        elif (
            s.state
            in (
                SubscribeState.NEW,
                SubscribeState.WAITING_LIST,
            )
            and s.matching_state not in MatchingState.MATCHED_STATES
        ):
            new_sub = s

    if not confirmed_sub or not new_sub:
        messages.error(
            request,
            "Could not identify the two roles: one subscription must be matched (NEW/CONFIRMED/PAID), "
            "the other must be unmatched (NEW/WAITING_LIST).",
        )
        return

    if confirmed_sub.course_id != new_sub.course_id:
        messages.error(request, "Both subscriptions must be for the same course.")
        return

    partner_sub = confirmed_sub.get_partner_subscription()
    if not partner_sub:
        messages.error(request, "The confirmed subscription has no partner.")
        return

    if not LeadFollow.is_compatible(new_sub.lead_follow, partner_sub.lead_follow):
        messages.error(
            request,
            f"Incompatible roles: {new_sub.user} ({new_sub.get_lead_follow_display()}) "
            f"and {partner_sub.user} ({partner_sub.get_lead_follow_display()}) cannot be matched.",
        )
        return

    if "switch_out" in request.POST:
        form = SwitchOutForm(request.POST)
        if form.is_valid():
            courses.services.matching.switch_out.switch_out_partner(
                confirmed_sub,
                new_sub,
                partner_sub,
                reason=form.cleaned_data["reason"],
                send_email=form.cleaned_data["send_email"],
            )
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = SwitchOutForm(
            initial={
                "_selected_action": list(
                    map(str, queryset.values_list("id", flat=True))
                )
            }
        )

    return render(
        request,
        "courses/auth/action_switch_out.html",
        {
            "confirmed_sub": confirmed_sub,
            "new_sub": new_sub,
            "partner_sub": partner_sub,
            "form": form,
        },
    )


def welcome_teachers(modeladmin, request, queryset):
    services.teachers.welcome_teachers(queryset, request)


@admin.action(description="Export confirmed subscriptions of selected courses as CSV")
def export_confirmed_subscriptions_csv(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, "csv")


@admin.action(
    description="Export confirmed subscriptions of selected courses as Google Contacts readable CSV"
)
def export_confirmed_subscriptions_csv_google(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, "csv_google")


@admin.action(description="Export confirmed subscriptions of selected courses as vCard")
def export_confirmed_subscriptions_vcard(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, "vcard")


@admin.action(description="Export confirmed subscriptions of selected courses as XLSX")
def export_confirmed_subscriptions_xlsx(modeladmin, request, queryset):
    ids = []
    for c in queryset:
        ids.append(c.id)
    return services.export_subscriptions(ids, "xlsx")


@admin.action(description="Export teacher payment information as CSV")
def export_teacher_payment_information_csv(modeladmin, request, queryset):
    return services.export_teacher_payment_information(offerings=queryset.all())


@admin.action(description="Export teacher payment information as Excel")
def export_teacher_payment_information_excel(modeladmin, request, queryset):
    return services.export_teacher_payment_information(
        offerings=queryset.all(), export_format="excel"
    )


def _build_voucher_email_preview(first_name, voucher_key, voucher_url):
    """Return (preview_html, None) with real values substituted, or None on error."""
    try:
        from post_office.models import EmailTemplate

        tmpl = EmailTemplate.objects.get(name="voucher")
        html = tmpl.html_content or ""
        return mark_safe(
            html.replace("{{ first_name }}", escape(first_name))
            .replace("{{ voucher_key }}", escape(voucher_key))
            .replace("{{ voucher_url }}", escape(voucher_url))
            .replace(
                "{{ custom_msg_de }}",
                '<span id="preview-msg-de" class="email-preview-highlight">'
                "[Ihre deutsche Nachricht hier]</span>",
            )
            .replace(
                "{{ custom_msg_en }}",
                '<span id="preview-msg-en" class="email-preview-highlight">'
                "[Your English message here]</span>",
            )
        )
    except Exception:
        return None


@admin.action(description="Mark selected vouchers as used")
def mark_voucher_as_used(modeladmin, request, queryset):
    # mark vouchers as used
    for voucher in queryset:
        voucher.mark_as_used(user=request.user, comment="by admin action")


@admin.action(description="Send a voucher to users of selected subscriptions")
def send_vouchers_for_subscriptions(modeladmin, request, queryset):
    form = None

    if "go" in request.POST:
        form = CreateSendVoucherForm(data=request.POST)

        if form.is_valid():
            recipients = [subscription.user for subscription in queryset]
            services.courses.create_send_vouchers(
                data=form.cleaned_data, recipients=recipients, user=request.user
            )
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = CreateSendVoucherForm(
            initial={
                "_selected_action": map(str, queryset.values_list("id", flat=True)),
                "voucher_comment": f"Sent to subscriptions to: {', '.join(list(set([subscription.course.name for subscription in queryset])))}",
            }
        )

    first_sub = queryset.first()
    first_user = first_sub.user if first_sub else None
    email_preview_html = _build_voucher_email_preview(
        first_name=first_user.first_name if first_user else "—",
        voucher_key="(generated on send)",
        voucher_url="#",
    )
    preview_hint = (
        f"Preview based on {first_user.get_full_name()}" if first_user else None
    )

    context = {
        "form": form,
        "action": "send_vouchers_for_subscriptions",
        "email_preview_html": email_preview_html,
        "preview_hint": preview_hint,
    }
    return render(request, "courses/auth/action_send_voucher.html", context)


@admin.action(description="Admit selected subscription(s) from waiting list")
def admit_from_waiting_list(modeladmin, request, queryset: list[Subscribe]) -> None:
    counter = 0
    for s in queryset:
        if s.state == SubscribeState.WAITING_LIST:
            with reversion.create_revision():
                s.state = SubscribeState.NEW
                s.save()
                counter += 1

                reversion.set_comment("Subscription admitted from the waiting list")
        else:
            messages.add_message(
                request, messages.WARNING, f"{s} is not on the waiting list. Skipped."
            )
    if counter:
        messages.add_message(
            request,
            messages.SUCCESS,
            f"{counter} subscribes admitted from the waiting list",
        )


@admin.action(description="Move selected subscription(s) to waiting list")
def move_to_waiting_list(modeladmin, request, queryset: list[Subscribe]) -> None:
    form = None
    if "go" in request.POST:
        form = MoveToWaitingListForm(request.POST)
        if form.is_valid():
            send_email = form.cleaned_data["send_email"]
            services.subscriptions.move_subscriptions_to_waiting_list(
                queryset, send_email, request
            )
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        selected_action = map(str, queryset.values_list("id", flat=True))
        form = MoveToWaitingListForm(initial={"_selected_action": selected_action})

    context = {
        "form": form,
        "action": "move_to_waiting_list",
    }
    return render(request, "courses/auth/action_move_to_waiting_list.html", context)


@admin.action(description="Send an email to subscriptions of the selected course(s)")
def send_course_email(modeladmin, request, queryset) -> HttpResponse:
    form = None

    if "go" in request.POST:
        form = SendCourseEmailForm(data=request.POST)

        if form.is_valid():
            services.courses.send_course_email(data=form.cleaned_data, courses=queryset)
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = SendCourseEmailForm(
            initial={
                "_selected_action": map(str, queryset.values_list("id", flat=True))
            }
        )

    return render(
        request,
        "courses/auth/action_send_course_email.html",
        {"courses": queryset, "evaluate_form": form},
    )


@admin.action(description="raise price to pay to fit amount")
def raise_price_to_pay(modeladmin, request, queryset):
    for subscription_payment in queryset:
        subscription: Subscribe = subscription_payment.subscription
        balance = subscription.sum_of_payments() - subscription.price_after_reductions()
        if balance > 0:
            subscription.price_to_pay += balance
            subscription.save()


@admin.action(description="List emails of selected subscribers")
def emaillist(modeladmin, request, queryset):
    form = None

    if "ok" in request.POST:
        form = EmailListForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect(reverse("admin:courses_subscribe_changelist"))

    if not form:
        form = EmailListForm()

    return render(
        request,
        "courses/auth/action_emaillist.html",
        {
            "form": form,
            "emails": [s.user.email + ";" for s in queryset.all()],
            "message": "Email addresses of selected subscribers (note that selected filters are applied!)",
        },
    )


@admin.action(description="List emails of accepted participants")
def offering_emaillist(modeladmin, request, queryset):
    form = None

    if "ok" in request.POST:
        form = EmailListForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect(reverse("admin:courses_offering_changelist"))

    if not form:
        form = EmailListForm()

    subscriptions = Subscribe.objects.accepted().filter(
        course__offering__in=queryset.all()
    )
    return render(
        request,
        "courses/auth/action_emaillist.html",
        {
            "form": form,
            "emails": [s.user.email for s in subscriptions],
            "message": "Email addresses of accepted subscribers of offerings {}".format(
                ", ".join(map(str, queryset.all()))
            ),
        },
    )


def make_inactive(modeladmin, request, queryset):
    for user in queryset:
        user.is_active = False
        user.save()
    messages.add_message(
        request, messages.SUCCESS, "Deactivated {} profiles".format(queryset.count())
    )


@admin.action(description="Export selected vouchers as CSV")
def export_vouchers_csv(modeladmin, request, queryset):
    keys = []
    for c in queryset:
        keys.append(c.key)
    return services.export_vouchers(keys, "csv")


@admin.action(description="Export selected vouchers as XLSX")
def export_vouchers_xlsx(modeladmin, request, queryset):
    keys = []
    for c in queryset:
        keys.append(c.key)
    return services.export_vouchers(keys, "xlsx")


@admin.action(description="Email selected voucher(s)")
def email_vouchers(modeladmin, request, queryset):
    form = None
    vouchers_with_users = [voucher for voucher in queryset if voucher.sent_to]
    vouchers_without_users = [voucher for voucher in queryset if not voucher.sent_to]

    if "go" in request.POST:
        form = SendVoucherEmailForm(data=request.POST)

        if form.is_valid():
            services.courses.email_vouchers(
                data=form.cleaned_data, vouchers=vouchers_with_users
            )
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = SendVoucherEmailForm(
            initial={
                "_selected_action": map(str, queryset.values_list("id", flat=True))
            }
        )

    first_v = queryset.filter(sent_to__isnull=False).first()
    if first_v is None:
        first_v = queryset.first()
    first_user = first_v.sent_to if first_v else None
    voucher_url = first_v.pdf_file.url if first_v and first_v.pdf_file else "#"
    email_preview_html = _build_voucher_email_preview(
        first_name=first_user.first_name if first_user else "—",
        voucher_key=first_v.key if first_v else "—",
        voucher_url=voucher_url,
    )
    preview_hint = (
        f"Preview based on {first_user.get_full_name()} – voucher {first_v.key}"
        if first_user
        else None
    )

    context = {
        "form": form,
        "action": "email_vouchers",
        "vouchers_without_user": [voucher.key for voucher in vouchers_without_users],
        "email_preview_html": email_preview_html,
        "preview_hint": preview_hint,
    }
    return render(request, "courses/auth/action_send_email_voucher.html", context)


@admin.action(description="Download selected voucher(s)")
def download_vouchers(modeladmin, request, queryset: QuerySet[Voucher]) -> HttpResponse:
    if queryset.count() == 1:
        voucher = queryset.first()
        response = HttpResponse(voucher.pdf_file.file, content_type="application/pdf")
        response["Content-Disposition"] = (
            f"attachment; filename=Voucher_{voucher.key}.pdf"
        )
        return response

    if "download" in request.POST:
        fmt = request.POST.get("format", "pdf")

        if fmt == "zip":
            # Spool to disk past 10 MB to avoid holding many PDFs in RAM at once.
            spooled = tempfile.SpooledTemporaryFile(max_size=10 * 1024 * 1024)
            with zipfile.ZipFile(spooled, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for voucher in queryset.iterator(chunk_size=50):
                    with (
                        voucher.pdf_file.file.open("rb") as src,
                        zip_file.open(f"Voucher_{voucher.key}.pdf", "w") as dst,
                    ):
                        shutil.copyfileobj(src, dst, length=64 * 1024)
            spooled.seek(0)
            response = FileResponse(spooled, content_type="application/zip")
            response["Content-Disposition"] = 'attachment; filename="vouchers.zip"'
            return response

        # fmt == "pdf": merge all pages into a single PDF
        from io import BytesIO

        from pypdf import PdfReader, PdfWriter

        writer = PdfWriter()
        for voucher in queryset.iterator(chunk_size=50):
            with voucher.pdf_file.open("rb") as src:
                writer.append(PdfReader(src))
        buf = BytesIO()
        writer.write(buf)
        buf.seek(0)
        response = FileResponse(buf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="vouchers.pdf"'
        return response

    # First call: show intermediate form so the user can choose ZIP vs single PDF
    form = DownloadVouchersForm(
        initial={"_selected_action": list(queryset.values_list("id", flat=True))}
    )
    return render(
        request,
        "courses/auth/action_download_vouchers.html",
        {
            "form": form,
            "action": "download_vouchers",
            "count": queryset.count(),
        },
    )
