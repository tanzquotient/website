from courses import models as models
from courses.services.general import log
from courses.utils import export


def export_subscriptions(course_ids, export_format):

    export_data = []
    for course_id in course_ids:
        course_name = models.Course.objects.get(id=course_id).name
        subscriptions = models.Subscribe.objects.accepted().filter(course_id=course_id).order_by('user__first_name')

        data = []
        if export_format == 'csv_google':
            data.append(['Given Name', 'Family Name', 'Gender',
                         'E-mail 1 - Type', 'E-mail 1 - Value', 'Phone 1 - Type', 'Phone 1 - Value'])
            for s in subscriptions:
                data.append([s.user.first_name, s.user.last_name, s.user.profile.gender, '* Private', s.user.email,
                             '* Private', s.user.profile.phone_number])

        if export_format == 'vcard':
            data = [subscription.user for subscription in subscriptions]
        else:
            data.append(['Vorname', 'Nachname', 'Lead/Follow', 'Partner', 'E-Mail', 'Mobile'])

            for s in subscriptions:
                data.append([s.user.first_name, s.user.last_name, s.get_lead_follow_text(), s.get_partner_name(),
                             s.user.email, s.user.profile.phone_number])

        export_data.append({'name': course_name, 'data': data})

    if len(export_data) == 0:
        return None

    if len(export_data) == 1:
        course_name = export_data[0]['name']
        return export(export_format, title='Kursteilnehmer-{}'.format(course_name), data=export_data[0]['data'])

    return export(export_format, title="Kursteilnehmer", data=export_data, multiple=True)


def export_summary(export_format='csv', offerings=models.Offering.objects.all()):
    """exports a summary of all offerings with room usage, course/subscription numbers"""

    offering_ids = [o.pk for o in offerings]
    subscriptions = models.Subscribe.objects.accepted().filter(course__offering__in=offering_ids)

    filename = 'TQ-Room Usage-{}'.format(offerings[0].name if len(offerings) == 1 else "Multiple Offerings")
    export_data = []

    rooms = models.Room.objects.all()

    header = ['', 'TOTAL']
    header += [room.name for room in rooms]

    export_data.append(header)

    row = ['TOTAL', subscriptions.count()]
    row += [subscriptions.filter(course__room=room).count() for room in rooms]

    export_data.append(row)

    for offering in offerings:
        subs = models.Subscribe.objects.accepted().filter(course__offering=offering)
        row = [offering.name, subs.count()]
        row += [subs.filter(course__room=room).count() for room in rooms]
        export_data.append(row)

    return export(export_format, title=filename, data=export_data)


def export_teacher_payment_information(export_format='csv', offerings=models.Offering.objects.all()):
    """Exports a summary of the given ``offerings`` concerning payment of teachers.

    Contains profile data relevant for payment of teachers and how many lesson at what rate to be paid.

    :param export_format: export format
    :param offerings: offerings to include in summary
    :return: response or ``None`` if format not supported
    """
    offering_ids = [o.pk for o in offerings]
    teachs = models.Teach.objects.filter(course__offering__in=offering_ids)
    teachers = {teach.teacher for teach in teachs.all()}
    teachers = sorted(teachers, key=lambda t: t.last_name)

    filename = 'TQ-Salary-{}'.format(offerings[0].name if len(offerings) == 1 else "Multiple Offerings")

    export_data = []

    header = ['User ID', 'First Name', 'Family Name', 'Gender', 'E-mail', 'Phone']
    header += ['Street', 'PLZ', 'City', 'Country']
    header += ['Birthdate', 'Nationality', 'Residence Permit', 'AHV Number', 'IBAN', 'Bank']
    for o in offerings:
        header += ['Wage for ' + o.name]

    export_data.append(header)

    for user in teachers:
        row = [user.id, user.first_name, user.last_name, user.profile.gender, user.email,
               user.profile.phone_number]
        if user.profile.address:
            row += [user.profile.address.street, user.profile.address.plz, user.profile.address.city,
                    str(user.profile.address.country)]
        else:
            row += ["-"] * 4

        row += [user.profile.birthdate, str(user.profile.nationality), user.profile.residence_permit, user.profile.ahv_number]

        if user.profile.bank_account:
            row += [user.profile.bank_account.iban, user.profile.bank_account.bank_info_str()]
        else:
            row += ["-"] * 2

        # wages for each offering separately
        for o in offerings:
            offering_teacher_teachs = teachs.filter(course__offering=o, teacher=user).all()
            log.debug(list(offering_teacher_teachs))
            wage = 0
            for teach in offering_teacher_teachs:
                wage += teach.get_wage()
            row.append(wage)

        export_data.append(row)

    return export(export_format, title=filename, data=export_data)