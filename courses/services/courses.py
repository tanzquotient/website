from courses import models as models
from courses.models import Voucher
from courses.services import get_subsequent_offering
from courses.services.general import log
from email_system.services import send_all_emails
from payment.vouchergenerator import generate_voucher_pdf
from survey.models import SurveyInstance
from tq_website import settings


def copy_course(course, to=None, set_preceeding_course=False):
    old_course_pk = course.pk
    if to is None:
        to = get_subsequent_offering()
    if to is not None:
        course_copy = course.copy()
        course_copy.offering = to
        course_copy.active = False
        course_copy.save()

        if set_preceeding_course:
            cs = models.CourseSuccession(predecessor=models.Course.objects.get(pk=old_course_pk), successor=course)
            cs.save()


def send_course_email(data, courses):
    email_template = data['email_template']
    email_subject = data['email_subject']
    email_content = data['email_content']
    send_to_participants = data['send_to_participants']
    send_to_teachers = data['send_to_teachers']
    survey = data['survey']
    survey_url_expire_date = data['survey_url_expire_date']

    emails = []

    for course in courses:
        recipients = []
        if send_to_participants:
            recipients += [p.user for p in course.participatory().all()]
        if send_to_teachers:
            recipients += course.get_teachers()

        for recipient in recipients:

            # Get context for email
            context = {
                'first_name': recipient.first_name,
                'last_name': recipient.last_name,
                'course': course.type.name,
                'offering': course.offering.name,
            }

            if survey:
                survey_instance = SurveyInstance.objects.create(
                    survey=survey,
                    email_template=email_template,
                    course=course,
                    user=recipient,
                    url_expire_date=survey_url_expire_date
                )
                context['survey_url'] = survey_instance.create_full_url()
                context['survey_expiration'] = survey_instance.url_expire_date

            subject = email_subject or email_template.subject
            html_message = email_content or email_template.html_content

            emails.append(dict(
                recipients=[recipient.email],
                sender=settings.DEFAULT_FROM_EMAIL,
                subject=subject,
                html_message=html_message,
                context=context,
            ))

    log.info('Sending {} emails'.format(len(emails)))
    send_all_emails(emails)


def send_vouchers(data, recipients):
    percentage = data['percentage']
    purpose = data['purpose']
    expires_flag = data['expires_flag']
    expires = data['expires']

    emails = []

    for recipient in recipients:
        voucher = Voucher(purpose=purpose, percentage=percentage, expires=expires if expires_flag else None)
        voucher.save()
        generate_voucher_pdf(vouchers=[voucher])

        email_context = {
            'first_name': recipient.first_name,
            'last_name': recipient.last_name,
            'voucher_key': voucher.key,
            'voucher_url': voucher.pdf_file.url,
        }

        emails.append(dict(
            recipients=[recipient.email],
            sender=settings.DEFAULT_FROM_EMAIL,
            template='voucher',
            context=email_context,
            attachments={'Voucher.pdf': voucher.pdf_file.file}
        ))

    log.info('Sending {} emails'.format(len(emails)))
    send_all_emails(emails)