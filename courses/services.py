import re
import unicodedata
import uuid
from datetime import date

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, Prefetch
from django.http import Http404, HttpResponseServerError
from django.utils import dateformat
from django.utils.translation import ugettext as _

import courses.models as models
from courses.models import Offering, OfferingType, Course, Weekday, IrregularLesson, RegularLesson, \
    RegularLessonException, Subscribe, UserProfile, MatchingState
from courses.utils import export
from utils.translation_utils import TranslationUtils
from .emailcenter import *
from .managers import CourseManager

log = logging.getLogger('tq')


# Create your services here.
def get_all_offerings():
    return models.Offering.objects.order_by('period__date_from', '-active')


def get_offerings_to_display(request=None, force_preview=False, only_regular_offerings=False):
    """return offerings that have display flag on and order them by start date in ascending order"""

    queryset = Offering.objects.select_related('period').prefetch_related('period__cancellations')
    if only_regular_offerings:
        queryset = queryset.filter(type=OfferingType.REGULAR)

    if force_preview or (request and request.user.is_staff):
        queryset = queryset.filter(Q(display=True) | Q(period__date_to__gte=date.today()))
    else:
        queryset = queryset.filter(display=True)

    return queryset.order_by('period__date_from')


def get_historic_offerings(offering_type=None):

    queryset = Offering.objects.all()
    if offering_type:
        queryset = Offering.objects.filter(type=offering_type)

    offerings = [o for o in queryset if o.is_historic() and o.has_date_from()]
    offerings_dict = {}

    for offering in offerings:
        year = offering.get_start_year()
        if year not in offerings_dict:
            offerings_dict[year] = []
        offerings_dict[year].append(offering)

    return sorted([(k, v) for k, v in offerings_dict.items()], key=lambda t: t[0], reverse=True)



def get_sections(offering, course_filter=None):
    offering_sections = []
    course_set = offering.course_set.select_related('period', 'type', 'room').prefetch_related(
        'regular_lessons',
        Prefetch('irregular_lessons', queryset=IrregularLesson.objects.order_by('date', 'time_from')),
        Prefetch('regular_lessons__exceptions', queryset=RegularLessonException.objects.order_by('date')),
        'period__cancellations',
    )

    if not course_filter:
        course_filter = lambda c: True

    if offering.type == OfferingType.REGULAR:
        for (w, w_name) in Weekday.CHOICES:
            courses_on_weekday = [c for c in CourseManager.weekday(course_set, w) if course_filter(c)]
            if courses_on_weekday:
                offering_sections.append({
                    'section_title': Weekday.WEEKDAYS_TRANSLATIONS_DE[w],
                    'courses': courses_on_weekday
                })

        courses_without_weekday = [c for c in CourseManager.weekday(course_set, None) if course_filter(c)]
        if courses_without_weekday:
            offering_sections.append({'section_title': _("Irregular weekday"), 'courses': courses_without_weekday})

    elif offering.type == OfferingType.IRREGULAR:
        courses_by_month = CourseManager.by_month(course_set)
        for (d, courses) in courses_by_month:
            if d is None:
                section_title = _("Unknown month")
            elif 1 < d.month < 12:
                # use the django formatter for date objects
                section_title = dateformat.format(d, 'F Y')
            else:
                section_title = ""
            # filter out undisplayed courses if not staff user
            courses = [c for c in courses if course_filter(c)]
            # tracks if at least one period of a course is set (it should be displayed on page)
            deviating_period = False
            for c in courses:
                if c.period:
                    deviating_period = True
                    break

            if courses:
                offering_sections.append(
                    {'section_title': section_title, 'courses': courses, 'hide_period_column': not deviating_period})
    else:
        message = "unsupported offering type"
        log.error(message)
        raise Http404(message)

    return offering_sections


def get_upcoming_courses_without_offering():
    courses = Course.objects.filter(
        display=True, offering__isnull=True
    )

    return [course for course in courses if not course.is_over()]


def get_current_active_offering():
    return models.Offering.objects.filter(active=True).order_by('period__date_from').first()


def get_subsequent_offering():
    res = models.Offering.objects.filter(period__date_from__gte=date.today()).order_by(
        'period__date_from').all()
    if len(res) > 0:
        return res[0]
    else:
        return None


def update_user(user, user_data):
    if 'email' in user_data:
        user.email = user_data['email']
    if 'first_name' in user_data:
        user.first_name = user_data['first_name']
    if 'last_name' in user_data:
        user.last_name = user_data['last_name']
    user.save()

    profile = get_or_create_userprofile(user)

    # convenience method. if key is not given, assume same as attr
    def set_if_given(attr, key=None):
        if not key:
            key = attr
        if key in user_data:
            setattr(profile, attr, user_data[key])

    set_if_given('legi')
    set_if_given('gender')
    set_if_given('phone_number')
    set_if_given('student_status')
    set_if_given('body_height')
    set_if_given('newsletter')
    set_if_given('get_involved')

    if not user_data["picture"]:
        profile.picture = None
    else:
        name = user_data['picture'].name
        user_data['picture'].name = "{}.{}".format(uuid.uuid4(), name.split(".")[-1])
        set_if_given('picture')
    set_if_given('about_me')

    set_if_given('birthdate')
    set_if_given('nationality')
    set_if_given('residence_permit')
    set_if_given('ahv_number')

    if all((key in user_data) for key in ['street', 'plz', 'city']):
        if profile.address:
            profile.address.street = user_data['street']
            profile.address.plz = user_data['plz']
            profile.address.city = user_data['city']
            profile.address.save()
        else:
            profile.address = models.Address.objects.create_from_user_data(user_data)

    if all((key in user_data) for key in ['iban']):
        if profile.bank_account:
            profile.bank_account.iban = user_data['iban']
            profile.bank_account.bank_name = user_data['bank_name']
            profile.bank_account.bank_zip_code = user_data['bank_zip_code']
            profile.bank_account.bank_city = user_data['bank_city']
            profile.bank_account.bank_country = user_data['bank_country']
            profile.bank_account.save()
        else:
            profile.bank_account = models.BankAccount.objects.create_from_user_data(user_data)

    profile.save()

    return user


def find_unused_username_variant(name, ignore=None):
    un = name
    i = 1
    while User.objects.exclude(username=ignore).filter(username=un).count() > 0:
        un = name + str(i)
        i += 1
    return un


def clean_username(name):
    '''first try to find ascii similar character, then strip away disallowed characters still left'''
    name = unicodedata.normalize('NFKD', name)
    return re.sub('[^0-9a-zA-Z+-.@_]+', '', name)


@transaction.atomic
def subscribe(course_id, data):
    """Actually enrols a user or a pair of users in a course"""

    # Get course and user
    course = Course.objects.get(id=course_id)
    user = data['user']

    # Get partner, if specified
    partner = None
    partner_email = data['partner_email']
    if partner_email:
        # Try to find by email address
        partner = User.objects.filter(email=partner_email)
        if not partner.exists():
            return dict(
                tag='danger',
                text=_('Partner does not exist!'),
                long_text=_('The email you specified does not belong to any user. Make sure your partner has an active account.')
            )

        # Get user object for partner
        partner = partner.first()

    # Find existing subscriptions
    user_subscription = course.subscriptions.filter(user=user)
    partner_subscription = course.subscriptions.filter(user=partner)

    # Errors
    if user == partner:
        return dict(
            tag='danger',
            text=_('You entered yourself as partner! Please enter a valid partner.')
        )
    if partner_subscription.exists() and partner_subscription.get().partner not in [None, user]:
        return dict(
            tag='danger',
            text=_('The partner you entered is already subscribed with someone else!')
        )
    if user_subscription.exists() and partner is None:
        return dict(
            tag='warning',
            text=_('You are already subscribed!')
        )
    if user_subscription.exists() and partner_subscription.exists():
        # Link partners if not already done
        if user_subscription.get().partner is None and partner_subscription.get().partner is None:
            user_subscription.get().partner = partner
            partner_subscription.get().partner = user
            user_subscription.get().matching_state = MatchingState.COUPLE
            partner_subscription.get().matching_state = MatchingState.COUPLE
        return dict(
            tag='warning',
            text=_('Both, you and your partner are already subscribed!')
        )


    # Get relevant info
    experience = data['experience']
    comment = data['comment']

    # Get or create user subscription
    if not user_subscription.exists():
        user_subscription = Subscribe(user=user, course=course, experience=experience, comment=comment)
    else:
        user_subscription = user_subscription.get()

    # Handle couple subscription
    if partner:
        # Get or create partner subscription
        if not partner_subscription.exists():
            partner_subscription = Subscribe(user=partner, course=course, experience=experience, comment=comment)
        else:
            partner_subscription = partner_subscription.get()

        # Link subscriptions
        user_subscription.partner = partner
        partner_subscription.partner = user
        user_subscription.matching_state = MatchingState.COUPLE
        partner_subscription.matching_state = MatchingState.COUPLE

        # Finish partner subscription
        partner_subscription.save()
        send_subscription_confirmation(partner_subscription)


    # Finish user subscription
    user_subscription.derive_matching_state()
    user_subscription.save()
    send_subscription_confirmation(user_subscription)

    return dict(
        tag='success',
        text=_('Successfully subscribed'),
        long_text=_('You will receive an email shortly')
    )


# creates a copy of course and sets its offering to the next offering in the future
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


# matches partners within the same course, considering their subscription time (fairness!) and respects also body_height (second criteria)
DEFAULT_BODY_HEIGHT = 170


def match_partners(subscriptions, request=None):
    courses = subscriptions.values_list('course', flat=True)
    match_count = 0
    for course_id in courses:
        single = subscriptions.filter(course__id=course_id, partner__isnull=True).all().exclude(
            state=models.SubscribeState.REJECTED)
        sm = single.filter(user__profile__gender=models.Gender.MEN).order_by('date').all()
        sw = single.filter(user__profile__gender=models.Gender.WOMAN).order_by('date').all()
        c = min(sm.count(), sw.count())
        sm = list(sm[0:c])  # list() enforces evaluation of queryset
        sw = list(sw[0:c])
        sm.sort(key=lambda
            x: x.user.profile.body_height if x.user.profile and x.user.profile.body_height else DEFAULT_BODY_HEIGHT)
        sw.sort(key=lambda
            x: x.user.profile.body_height if x.user.profile and x.user.profile.body_height else DEFAULT_BODY_HEIGHT)
        while c > 0:
            c = c - 1
            m = sm[c]
            w = sw[c]
            m.partner = w.user
            m.matching_state = models.MatchingState.MATCHED
            m.save()
            w.partner = m.user
            w.matching_state = models.MatchingState.MATCHED
            w.save()
            match_count += 1
    if match_count:
        messages.add_message(request, messages.SUCCESS,
                             _(u'{} couples matched successfully').format(match_count))


def correct_matching_state_to_couple(subscriptions, request=None):
    corrected_count = 0

    for s in subscriptions.all():
        partner_subs = subscriptions.filter(user=s.partner, course=s.course)
        if partner_subs.count() == 1:
            partner_sub = partner_subs.first()
            # because we update matching state iteratively, we have to allow also COUPLE State
            allowed_states = [models.MatchingState.MATCHED, models.MatchingState.COUPLE]
            if s.matching_state == models.MatchingState.MATCHED and partner_sub.matching_state in allowed_states:
                s.matching_state = models.MatchingState.COUPLE
                s.save()
                corrected_count += 1

    if corrected_count:
        messages.add_message(request, messages.SUCCESS,
                             _(u'{} subscriptions ({} couples) corrected successfully').format(corrected_count,
                                                                                               corrected_count / 2))


def unmatch_partners(subscriptions, request):
    corrected_count = 0
    invalid_state_count = 0
    invalid_matching_state_count = 0
    for s in subscriptions.all():
        if s.state == models.SubscribeState.NEW:
            allowed_states = [models.MatchingState.MATCHED]
            partner_subs = subscriptions.filter(user=s.partner, course=s.course)
            if partner_subs.count() == 1 and s.matching_state in allowed_states and partner_subs.first().matching_state in allowed_states:
                _unmatch_person(s)
                _unmatch_person(partner_subs.first())
                corrected_count += 1
            else:
                invalid_matching_state_count += 1
        else:
            invalid_state_count += 1

    invalid_matching_state_count -= corrected_count  # subtract wrongly counted errors

    if corrected_count:
        messages.add_message(request, messages.SUCCESS,
                             _(u'{} couples unmatched successfully').format(corrected_count))
    if invalid_state_count:
        messages.add_message(request, messages.WARNING,
                             _(u'{} subscriptions can not be unmatched because already CONFIRMED').format(
                                 invalid_state_count))
    if invalid_matching_state_count:
        messages.add_message(request, messages.WARNING,
                             _(u'{} subscriptions can not be unmatched because invalid matching state').format(
                                 invalid_matching_state_count))


def breakup_couple(subscriptions, request):
    corrected_count = 0
    invalid_state_count = 0
    invalid_matching_state_count = 0
    for s in subscriptions.all():
        if s.state == models.SubscribeState.NEW:
            allowed_states = [models.MatchingState.COUPLE]
            partner_subs = subscriptions.filter(user=s.partner, course=s.course)
            if partner_subs.count() == 1 and s.matching_state in allowed_states and partner_subs.first().matching_state in allowed_states:
                _unmatch_person(s)
                _unmatch_person(partner_subs.first())
                corrected_count += 1
            else:
                invalid_matching_state_count += 1
        else:
            invalid_state_count += 1

    invalid_matching_state_count -= corrected_count  # subtract wrongly counted errors

    if corrected_count:
        messages.add_message(request, messages.SUCCESS,
                             _(u'{} couples broken up successfully').format(corrected_count))
    if invalid_state_count:
        messages.add_message(request, messages.WARNING,
                             _(u'{} couples can not be broken up because already CONFIRMED').format(
                                 invalid_state_count))
    if invalid_matching_state_count:
        messages.add_message(request, messages.WARNING,
                             _(u'{} couples can not be broken up because invalid matching state').format(
                                 invalid_matching_state_count))


def _unmatch_person(subscription):
    subscription.partner = None
    subscription.matching_state = models.MatchingState.TO_REMATCH
    subscription.save()


class NoPartnerException(Exception):
    def __str__(self):
        return 'This subscription has no partner set'


def confirm_subscription(subscription, request=None, allow_single_in_couple_course=False):
    '''sends a confirmation mail if subscription is confirmed (by some other method) and no confirmation mail was sent before'''
    # check: only people with partner are confirmed (in couple courses)
    if not allow_single_in_couple_course and subscription.course.type.couple_course and subscription.partner is None:
        raise NoPartnerException()

    if subscription.state == models.SubscribeState.NEW:
        subscription.state = models.SubscribeState.CONFIRMED
        subscription.save()

        m = send_participation_confirmation(subscription)
        if m:
            # log that we sent the confirmation
            c = models.Confirmation(subscription=subscription, mail=m)
            c.save()
            return True
        else:
            return False
    else:
        return False


# same as confirm_subscription, but for multiple subscriptions at once
MESSAGE_NO_PARTNER_SET = _(u'{} subscriptions were not confirmed because no partner set')


def confirm_subscriptions(subscriptions, request=None, allow_single_in_couple_course=False):
    no_partner_count = 0
    confirmed_count = 0
    for subscription in subscriptions:
        try:
            if confirm_subscription(subscription, request, allow_single_in_couple_course):
                confirmed_count += 1
        except NoPartnerException as e:
            no_partner_count += 1

    if no_partner_count:  # if any subscriptions not confirmed due to missing partner
        log.warning(MESSAGE_NO_PARTNER_SET.format(no_partner_count))
        if request:
            messages.add_message(request, messages.WARNING, MESSAGE_NO_PARTNER_SET.format(no_partner_count))
    if confirmed_count:
        messages.add_message(request, messages.SUCCESS,
                             _(u'{} of {} confirmed successfully').format(confirmed_count, len(subscriptions)))


def unconfirm_subscriptions(subscriptions, request=None):
    for s in subscriptions.all():
        if s.state == models.SubscribeState.CONFIRMED:
            s.state = models.SubscribeState.NEW
            s.save()


def reject_subscription(subscription, reason=None, send_email=True):
    '''sends a rejection mail if subscription is rejected (by some other method) and no rejection mail was sent before'''
    subscription.state = models.SubscribeState.REJECTED
    subscription.save()
    if not reason:
        reason = detect_rejection_reason(subscription)
    c = models.Rejection(subscription=subscription, reason=reason, mail_sent=False)
    c.save()

    if send_email and models.Rejection.objects.filter(subscription=subscription, mail_sent=True).count() == 0:
        # if ensures that no mail was ever sent due to a rejection to this user

        # save if we sent the mail
        c.mail = send_rejection(subscription, reason)
        c.mail_sent = c.mail is not None
        c.save()


def reject_subscriptions(subscriptions, reason=None, send_email=True):
    '''same as reject_subscription, but for multiple subscriptions at once'''
    for subscription in subscriptions:
        reject_subscription(subscription, reason, send_email)


def unreject_subscriptions(subscriptions, request=None):
    unrejected_count = 0
    for subscription in subscriptions:
        if subscription.state == models.SubscribeState.REJECTED:
            subscription.state = models.SubscribeState.NEW
            subscription.save()
            unrejected_count += 1
    if unrejected_count:
        messages.add_message(request, messages.SUCCESS,
                             _(u'{} unrejected successfully').format(unrejected_count))


def welcome_teacher(teach):
    if not teach.welcomed:
        teach.welcomed = True
        teach.save()

        m = send_teacher_welcome(teach)
        if m:
            # log that we sent the confirmation
            c = models.TeacherWelcome(teach=teach, mail=m)
            c.save()
            return True
        else:
            return False
    else:
        return False


def welcome_teachers(courses, request):
    count = 0
    total = 0
    for course in courses:
        for teach in course.teaching.all():
            total += 1
            if welcome_teacher(teach):
                count += 1
    messages.add_message(request, messages.SUCCESS,
                         _(u'{} of {} welcomed successfully').format(count, total))


def welcome_teachers_reset_flag(courses, request):
    count = 0
    total = 0
    for course in courses:
        for teach in course.teaching.all():
            if teach.welcomed:
                count += 1
                teach.welcomed = False
                teach.save()
            total += 1
    messages.add_message(request, messages.SUCCESS,
                         _(u'{} of {} teachers reset successfully').format(count, total))


def get_or_create_userprofile(user):
    try:
        return models.UserProfile.objects.get(user=user)
    except ObjectDoesNotExist:
        userprofile = models.UserProfile(user=user)
        return userprofile


def calculate_relevant_experience(user, course):
    '''finds a list of courses the "user" did already and that are somehow relevant for "course"'''
    relevant_exp = [style.id for style in course.type.styles.all()]
    return [s.course for s in
            models.Subscribe.objects.filter(user=user, state__in=models.SubscribeState.ACCEPTED_STATES,
                                            course__type__styles__id__in=relevant_exp).exclude(
                course=course).order_by('course__type__level').distinct().all()]


def format_prices(price_with_legi, price_without_legi, price_special=None):
    if price_special:
        return price_special
    elif price_with_legi and price_without_legi:
        if price_with_legi == price_without_legi:
            r = "{} CHF".format(price_with_legi.__str__())
        else:
            r = "mit Legi {} / sonst {} CHF".format(price_with_legi.__str__(), price_without_legi.__str__())
    elif price_without_legi:
        r = "mit Legi freier Eintritt (sonst {} CHF)".format(price_without_legi.__str__())
    else:
        r = None  # handle this case in template!
    return r


def model_attribute_language_fallback(model, attribute):
    return TranslationUtils.get_text_with_language_fallback(model, attribute)


INVALID_TITLE_CHARS = re.compile(r'[^\w\-_ ]', re.IGNORECASE | re.UNICODE)


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
            data.append(
                ['Vorname', 'Nachname', 'Geschlecht', 'E-Mail', 'Mobile', 'Legi-Nr.', 'Zu bezahlen', 'Erfahrung'])

            for s in subscriptions:
                data.append([s.user.first_name, s.user.last_name, s.user.profile.gender, s.user.email,
                             s.user.profile.phone_number, s.user.profile.legi, s.get_price_to_pay(), s.experience])

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
