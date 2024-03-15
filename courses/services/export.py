from typing import Iterable, Optional

from django.http import HttpResponse

from courses import models as models
from courses.admin import VoucherAdmin as VoucherAdmin
from utils import export


def export_subscriptions(
    course_ids: Iterable[int], export_format: str
) -> Optional[HttpResponse]:
    export_data = []
    for course_id in course_ids:
        course = models.Course.objects.get(id=course_id)
        subscriptions = (
            models.Subscribe.objects.accepted()
            .filter(course_id=course_id)
            .order_by("user__first_name")
        )

        data = []
        if export_format == "csv_google":
            data.append(
                [
                    "Given Name",
                    "Family Name",
                    "Gender",
                    "E-mail 1 - Type",
                    "E-mail 1 - Value",
                    "Phone 1 - Type",
                    "Phone 1 - Value",
                ]
            )
            for s in subscriptions:
                data.append(
                    [
                        s.user.first_name,
                        s.user.last_name,
                        s.user.profile.gender,
                        "* Private",
                        s.user.email,
                        "* Private",
                        s.user.profile.phone_number,
                    ]
                )

        if export_format == "vcard":
            data = [subscription.user for subscription in subscriptions]
        else:
            data.append(
                ["First name", "Last name", "E-Mail", "Mobile"]
                + (["Lead/Follow", "Partner"] if course.type.couple_course else [])
                + ["Student status", "Course fees"]
            )

            for s in subscriptions:
                data.append(
                    [
                        s.user.first_name,
                        s.user.last_name,
                        s.user.email,
                        s.user.profile.phone_number,
                    ]
                    + (
                        [s.get_assigned_role_str(), s.get_partner_name()]
                        if course.type.couple_course
                        else []
                    )
                    + [
                        "student" if s.user.profile.is_student() else "not a student",
                        s.price_to_pay,
                    ]
                )

        export_data.append({"name": course.name, "data": data})

    if len(export_data) == 0:
        return None

    if len(export_data) == 1:
        course_name = export_data[0]["name"]
        return export(
            export_format,
            title="Kursteilnehmer-{}".format(course_name),
            data=export_data[0]["data"],
        )

    return export(
        export_format, title="Kursteilnehmer", data=export_data, multiple=True
    )


def export_summary(export_format="csv", offerings=models.Offering.objects.all()):
    """exports a summary of all offerings with room usage, course/subscription numbers"""

    offering_ids = [o.pk for o in offerings]
    subscriptions = models.Subscribe.objects.accepted().filter(
        course__offering__in=offering_ids
    )

    filename = "Tanzquotient-Room Usage-{}".format(
        offerings[0].name if len(offerings) == 1 else "Multiple Offerings"
    )
    export_data = []

    rooms = models.Room.objects.all()

    header = ["", "TOTAL"]
    header += [room.name for room in rooms]

    export_data.append(header)

    row = ["TOTAL", subscriptions.count()]
    row += [subscriptions.filter(course__room=room).count() for room in rooms]

    export_data.append(row)

    for offering in offerings:
        subs = models.Subscribe.objects.accepted().filter(course__offering=offering)
        row = [offering.name, subs.count()]
        row += [subs.filter(course__room=room).count() for room in rooms]
        export_data.append(row)

    return export(export_format, title=filename, data=export_data)


def export_teacher_payment_information(
    export_format: str = "csv", offerings=models.Offering.objects.all()
):
    from payment import services

    export_name, personal_data, courses = services.offering_finance_teachers(offerings)
    return export(
        export_format,
        title=export_name,
        multiple=True,
        data=[
            dict(data=courses, name="Courses"),
            dict(data=personal_data, name="Personal Data"),
        ],
    )

def export_vouchers(
    voucher_keys: Iterable[int], export_format: str = "csv"
) -> Optional[HttpResponse]:

    vouchers = []
    for key in voucher_keys:
        vouchers.append(models.Voucher.objects.get(key=key))

    data = []
    data.append(
        [
            "Key",
            "Purpose",
            "Comment",
            "Percentage",
            "Amount",
            "Redeemed amount",
            "Issued",
            "Issuer",
            "Used timestamp",
            "Offering",
            "Course",
            "Redeemer",
            "Expires"
        ]
    )
    for v in vouchers:
        data.append(
            [
                v.key,
                v.purpose,
                v.comment,
                v.percentage,
                v.amount,
                VoucherAdmin.redeemed_amount(v),
                v.issued,
                VoucherAdmin.issuer(v),
                VoucherAdmin.used_timestamp(v),
                VoucherAdmin.offering(v),
                VoucherAdmin.course(v),
                VoucherAdmin.redeemer(v),
                v.expires
            ]
        )

    if len(data) == 0:
        return None

    return export(
        export_format, title="Vouchers", data=data, multiple=False
    )