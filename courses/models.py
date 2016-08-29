from django.db import models

import datetime
from reversion import revisions as reversion

from django.conf import settings

import django.contrib.auth as auth

from courses import managers
from django.core.exceptions import ValidationError
from djangocms_text_ckeditor.fields import HTMLField
import base36
import hashlib
import random, string
from django.db.models import Q
from django.db import transaction
import payment.vouchergenerator
from courses.emailcenter import send_online_payment_successful


class Weekday:
    MONDAY = 'mon'
    TUESDAY = 'tue'
    WEDNESDAY = 'wed'
    THURSDAY = 'thu'
    FRIDAY = 'fri'
    SATURDAY = 'sat'
    SUNDAY = 'sun'

    WEEKEND = [SATURDAY, SUNDAY]

    CHOICES = (('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'),
               ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'),
               ('sun', 'Sunday'))
    NUMBERS = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}


WEEKDAYS_TRANS = {'mon': 'Montag', 'tue': 'Dienstag', 'wed': 'Mittwoch', 'thu': 'Donnerstag', 'fri': 'Freitag',
                  'sat': 'Samstag', 'sun': 'Sonntag'}


class PaymentMethod:
    COUNTER = 'counter'
    COURSE = 'course'
    ONLINE = 'online'
    VOUCHER = 'voucher'

    CHOICES = (
        (COUNTER, 'counter'), (COURSE, 'course'), (ONLINE, 'online'), (VOUCHER, 'voucher'))


class Address(models.Model):
    street = models.CharField(max_length=255)
    plz = models.IntegerField()
    city = models.CharField(max_length=255)

    objects = managers.AddressManager()

    def equals(self, a):
        return self.street == a.street and self.plz == a.plz and self.city == a.city

    def __str__(self):
        return "{}, {} {}".format(self.street, self.plz, self.city)


class UserProfile(models.Model):
    class Gender:
        MEN = 'm'
        WOMAN = 'w'

        CHOICES = ((MEN, 'Men'), (WOMAN, 'Woman'))

    class StudentStatus:
        ETH = 'eth'
        UNI = 'uni'
        PH = 'ph'
        OTHER = 'other'
        NO = 'no'

        CHOICES = ((ETH, 'ETH'), (UNI, 'Uni'), (PH, 'PH'), (OTHER, 'Other'), (NO, 'Not a student'))

    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name='profile')
    user.help_text = "The user which is matched to this user profile."
    legi = models.CharField(max_length=16, blank=True, null=True)
    gender = models.CharField(max_length=1,
                              choices=Gender.CHOICES, blank=False, null=True,
                              default=None)
    address = models.ForeignKey(Address, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    student_status = models.CharField(max_length=10,
                                      choices=StudentStatus.CHOICES, blank=False, null=False,
                                      default=StudentStatus.NO)
    body_height = models.IntegerField(blank=True, null=True)
    body_height.help_text = "The user's body height in cm."
    newsletter = models.BooleanField(default=True)
    get_involved = models.BooleanField(default=False)
    get_involved.help_text = "If this user is interested to get involved with our organisation."

    about_me = HTMLField(blank=True, null=True)

    # convenience method for model user are added here
    def is_teacher(self):
        return self.user.teaching.count() > 0

    class Meta:
        permissions = (
            ("access_counterpayment", "Can access counter payment"),
        )

    def __str__(self):
        return "{}".format(self.user.get_full_name())


class Style(models.Model):
    name = models.CharField(max_length=30, unique=True, blank=False)
    description = HTMLField(blank=True, null=True)
    url_info = models.URLField(max_length=500, blank=True, null=True)
    url_info.help_text = "A url to an information page (e.g. Wikipedia)."
    url_video = models.URLField(max_length=500, blank=True, null=True)
    url_video.help_text = "A url to a demo video (e.g Youtube)."
    url_playlist = models.URLField(max_length=500, blank=True, null=True)
    url_playlist.help_text = "A url to a playlist (e.g on online-Spotify, Youtube)."

    def __str__(self):
        return "{}".format(self.name)


class Room(models.Model):
    name = models.CharField(max_length=30, unique=True, blank=False)
    description = HTMLField(blank=True, null=True)
    address = models.OneToOneField(Address, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    url.help_text = "The url to Google Maps (see https://support.google.com/maps/answer/144361?p=newmaps_shorturl&rd=1)"
    contact_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.name)


class Period(models.Model):
    date_from = models.DateField(blank=True, null=True)
    date_from.help_text = "The start date of this period. Can be left empty."
    date_to = models.DateField(blank=True, null=True)
    date_to.help_text = "The end date of this period. Can be left empty. If both are left empty, this period is displayed as 'on request'."

    def format_date(self, d):
        return d.strftime('%d. %b %Y')

    format_date.short_description = 'Period from/to'

    def __str__(self):
        if self.date_from and self.date_to:
            return "{} - {}".format(self.format_date(self.date_from), self.format_date(self.date_to))
        elif self.date_from:
            return "ab {}".format(self.format_date(self.date_from))
        elif self.date_to:
            return "bis {}".format(self.format_date(self.date_to))
        else:
            return "ganzjährlich"


class RegularLesson(models.Model):
    course = models.ForeignKey('Course', related_name='regular_lessons')
    weekday = models.CharField(max_length=3,
                               choices=Weekday.CHOICES,
                               default=None)
    time_from = models.TimeField()
    time_to = models.TimeField()

    def get_weekday_number(self):
        return Weekday.NUMBERS[self.weekday]

    def __str__(self):
        return "{}, {}-{}".format(WEEKDAYS_TRANS[self.weekday], self.time_from.strftime("%H:%M"),
                                  self.time_to.strftime("%H:%M"))


class RegularLessonCancellation(models.Model):
    course = models.ForeignKey('Course', related_name='cancellations')
    date = models.DateField(blank=False, null=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return "{}".format(self.date.strftime('%d.%m.%Y'))


class IrregularLesson(models.Model):
    course = models.ForeignKey('Course', related_name='irregular_lessons')
    date = models.DateField(blank=False, null=False)
    time_from = models.TimeField()
    time_to = models.TimeField()
    room = models.ForeignKey(Room, related_name='irregular_lessons', blank=True, null=True, on_delete=models.SET_NULL)
    room.help_text = "The room for this lesson. If left empty, the course room is assumed."

    class Meta:
        ordering = ['date', 'time_from']

    def __str__(self):
        s = "{}, {}-{}".format(self.date, self.time_from.strftime("%H:%M"),
                               self.time_to.strftime("%H:%M"))
        if self.room:
            s = s + ", {}".format(self.room)
        return s


class CourseType(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False)
    styles = models.ManyToManyField(Style, related_name='course_types', blank=True)
    level = models.IntegerField(default=None, blank=True, null=True)
    description = HTMLField(blank=True, null=True)
    couple_course = models.BooleanField(default=True)

    def get_level(self):
        return self.level if self.level else "";

    def format_styles(self):
        return ', '.join(map(str, self.styles.all()))

    format_styles.short_description = "Styles"

    def __str__(self):
        return "{}".format(self.name)


class PeriodCancellation(models.Model):
    course = models.ForeignKey('Period', related_name='cancellations')
    date = models.DateField(blank=False, null=True)

    def __str__(self):
        return "{}".format(self.date.strftime('%d.%m.%Y'))


class Course(models.Model):
    name = models.CharField(max_length=255, blank=False)
    name.help_text = "This name is just for reference and is not displayed anywhere on the website."
    type = models.ForeignKey(CourseType, related_name='courses', blank=False, null=False)
    type.help_text = "The name of the course type is displayed on the website as the course title ."
    room = models.ForeignKey(Room, related_name='courses', blank=True, null=True, on_delete=models.SET_NULL)
    min_subscribers = models.IntegerField(blank=False, null=False, default=6)
    max_subscribers = models.IntegerField(blank=True, null=True)
    price_with_legi = models.FloatField(blank=True, null=True, default=35)
    price_without_legi = models.FloatField(blank=True, null=True, default=70)
    price_special = models.CharField(max_length=255, blank=True, null=True)
    price_special.help_text = "Set this only if you want a different price schema."
    open_class = models.BooleanField(blank=True, null=False, default=False)
    open_class.help_text = "Open classes do not require a subscription or subscription is done via a different channel."
    period = models.ForeignKey(Period, blank=True, null=True, on_delete=models.SET_NULL)
    period.help_text = "You can set a custom period for this course here. If this is left empty, the period from the offering is taken."
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Teach', related_name='teaching_courses')
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Subscribe', related_name='courses',
                                         through_fields=('course', 'user'))
    offering = models.ForeignKey('Offering', blank=False, null=True, on_delete=models.SET_NULL)
    display = models.BooleanField(default=True)
    display.help_text = "Defines if this course should be displayed on the Website (if checked, course is displayed if offering is displayed)."
    active = models.BooleanField(default=True)
    active.help_text = "Defines if clients can subscribe to this course (if checked, course is active if offering is active)."
    special = HTMLField(blank=True, null=True)
    special.help_text = 'Any special properties of this course.'
    evaluated = models.BooleanField(default=False)
    evaluated.help_text = "If this course was evaluated by a survey or another way."

    objects = managers.CourseManager()

    def participatory(self):
        return self.subscriptions.accepted()

    def number_paid(self):
        return self.subscriptions.accepted().paid().count()

    def total_paid(self):
        total = 0.0
        for subscription in self.subscriptions.accepted().paid().all():
            total += subscription.get_price_to_pay()
        return total

    def total_paid_course(self):
        total = 0.0
        for subscription in self.subscriptions.accepted().paid().course_payment().all():
            total += subscription.get_price_to_pay()
        return total

    def total_price(self):
        total = 0.0
        for subscription in self.subscriptions.accepted().all():
            total += subscription.get_price_to_pay()
        return total

    def total_unpaid(self):
        return self.total_price() - self.total_paid()

    def format_teachers(self):
        return ', '.join(map(auth.get_user_model().get_full_name, self.teachers.all()))

    format_teachers.short_description = "Teachers"

    def format_prices(self):
        from courses.services import format_prices
        return format_prices(self.price_with_legi, self.price_without_legi, self.price_special)

    format_prices.short_description = "Prices"

    def get_period(self):
        if self.period is None:
            return self.offering.period
        else:
            return self.period

    # only show free_places_count if it can be calculated and is below 10
    def show_free_places_count(self):
        r = self.get_free_places_count()
        if r is not None and 0 < r < 10:
            return r
        else:
            return None

    def get_free_places_count(self):
        if self.max_subscribers != None:
            c = self.max_subscribers - self.subscriptions.accepted().count()
            if c > 0:
                return c
            else:
                return 0
        else:
            return None

    def get_confirmed_count(self):
        return self.subscriptions.accepted().count()

    def men_count(self):
        return self.subscriptions.men().count()

    def women_count(self):
        return self.subscriptions.women().count()

    def single_men_count(self):
        return self.subscriptions.single_men().count()

    def single_women_count(self):
        return self.subscriptions.single_women().count()

    def men_needed(self):
        return self.single_men_count() < self.single_women_count()

    def women_needed(self):
        return self.single_women_count() < self.single_men_count()

    def is_displayed(self, preview=False):
        if self.offering is None:
            return False
        else:
            return preview or (self.offering.display and self.display)  # both must be true to be displayed

    def is_preview(self):
        return not self.display or (self.offering is not None and self.offering.is_preview)

    def is_subscription_allowed(self):
        if self.open_class:
            return False
        else:
            if self.offering is None:
                return self.active
            else:
                return self.offering.active and self.active  # both must be true to allow subscription

    def get_lessons(self):
        lessons = []
        lessons.extend(self.regular_lessons.all())
        lessons.extend(self.irregular_lessons.all())
        return lessons

    def get_lessons_as_strings(self):
        return map(str, self.get_lessons())

    def format_lessons(self):
        return ' & '.join(self.get_lessons_as_strings())

    format_lessons.short_description = "Lessons"

    def get_cancellation_dates(self):
        # take the union of the cancellations of this course and the period it belongs to
        dates = [c.date for c in self.cancellations.all()]
        dates_offering = []
        if self.offering.period:
            dates_offering = [c.date for c in self.offering.period.cancellations.all()]
        return sorted(dates + dates_offering)

    def format_cancellations(self):
        dates = [d.strftime('%d.%m.%Y') for d in self.get_cancellation_dates()]
        return ' / '.join(dates)

    format_cancellations.short_description = "Cancellations"

    def get_first_regular_lesson(self):
        if self.regular_lessons.exists():
            return self.regular_lessons.all()[0]
        else:
            return None

    def get_first_irregular_lesson(self):
        if self.irregular_lessons.exists():
            return self.irregular_lessons.order_by('date', 'time_from').all()[0]
        else:
            return None

    def get_first_regular_lesson_date(self):
        def next_weekday(d, weekday):
            days_ahead = weekday - d.weekday()
            if days_ahead < 0:  # Target day already happened this week
                days_ahead += 7
            return d + datetime.timedelta(days_ahead)

        frl = self.get_first_regular_lesson()
        period = self.get_period()
        if frl is not None and period is not None:
            return next_weekday(period.date_from, frl.get_weekday_number())
        else:
            return None

    def get_first_irregular_lesson_date(self):
        fil = self.get_first_irregular_lesson()
        if fil is not None:
            return fil.date
        else:
            return None

    def get_first_lesson_date(self):
        d1 = self.get_first_irregular_lesson_date()
        d2 = self.get_first_regular_lesson_date()
        if d1 is None:
            if d2 is None:
                return None
            else:
                return d2
        else:
            if d2 is None:
                return d1
            else:
                if d1 < d2:
                    return d1
                else:
                    return d2

    # create and stores identical copy of this course
    def copy(self):
        old = Course.objects.get(pk=self.id)
        self.pk = None
        self.save()

        # copy regular lessons
        for lesson in old.regular_lessons.all():
            lesson.pk = None
            lesson.course = self
            lesson.save()

        # copy irregular lessons
        for lesson in old.irregular_lessons.all():
            lesson.pk = None
            lesson.course = self
            lesson.save()

        # copy cancellations
        for c in old.cancellations.all():
            c.pk = None
            c.course = self
            c.save()

        # copy teachers
        for teach in old.teaching.all():
            teach.pk = None
            teach.course = self
            teach.save()

        return self

    # position field for ordering columns (grappelli feature)
    position = models.PositiveSmallIntegerField("Position", default=0)

    class Meta:
        ordering = ['position', 'type__name', 'name']

    def __str__(self):
        return "{} ({})".format(self.name, self.offering)


@reversion.register()
class Subscribe(models.Model):
    class State:
        NEW = 'new'
        CONFIRMED = 'confirmed'
        PAYED = 'payed'
        COMPLETED = 'completed'
        REJECTED = 'rejected'
        TO_REIMBURSE = 'to_reimburse'
        CHOICES = (
            (NEW, 'new'), (CONFIRMED, 'confirmed (to pay)'), (PAYED, 'payed'), (COMPLETED, 'completed'),
            (REJECTED, 'rejected'), (TO_REIMBURSE, 'to reimburse'))

    class MatchingState:
        UNKNOWN = 'unknown'
        COUPLE = 'couple'
        TO_MATCH = 'to_match'
        TO_REMATCH = 'to_rematch'
        MATCHED = 'matched'
        NOT_REQUIRED = 'not_required'
        CHOICES = (
            (UNKNOWN, 'Unknown'), (COUPLE, 'Couple'), (TO_MATCH, 'To match'), (TO_REMATCH, 'To rematch'),
            (MATCHED, 'Matched'),
            (NOT_REQUIRED, 'Not required'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subscriptions')
    course = models.ForeignKey(Course, related_name='subscriptions')
    date = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    date.help_text = "The date/time when the subscription was made."
    partner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subscriptions_as_partner', blank=True,
                                null=True)
    matching_state = models.CharField(max_length=30,
                                      choices=MatchingState.CHOICES, blank=False, null=False,
                                      default=MatchingState.UNKNOWN)
    experience = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    comment.help_text = "A optional comment made by the user during subscription."

    state = models.CharField(max_length=30,
                             choices=State.CHOICES, blank=False, null=False,
                             default=State.NEW)
    usi = models.CharField(max_length=6, blank=True, null=False, default="------", unique=True)
    usi.help_text = "Unique subscription identifier: 4 characters identifier, 2 characters checksum"

    paymentmethod = models.CharField(max_length=30, choices=PaymentMethod.CHOICES, blank=True, null=True)

    objects = managers.SubscribeQuerySet.as_manager()

    def generate_usi(self):
        checksum = hashlib.md5()
        checksum.update(str(self.id).encode('utf-8'))
        return (base36.dumps(self.id).zfill(4)[:4] + checksum.hexdigest()[:2]).lower()

    def get_offering(self):
        return self.course.offering

    get_offering.short_description = "Offering"

    def get_user_gender(self):
        return self.user.profile.gender

    get_user_gender.short_description = "Gender"

    def get_user_email(self):
        return self.user.email

    get_user_email.short_description = "Email"

    def get_user_body_height(self):
        return self.user.profile.body_height

    get_user_body_height.short_description = "Body height"

    # returns similar courses that the user did before in the system
    def get_calculated_experience(self):
        from courses.services import calculate_relevant_experience
        return ', '.join(map(str, calculate_relevant_experience(self.user, self.course)))

    get_calculated_experience.short_description = "Calculated experience"

    def payed(self):
        return self.state == Subscribe.State.PAYED or self.state == Subscribe.State.TO_REIMBURSE or self.state == Subscribe.State.COMPLETED

    # returns similar courses that the user did before in the system
    def get_payment_state(self):
        c = self.user.subscriptions.filter(state=Subscribe.State.CONFIRMED, course__offering__active=False).filter(
            ~Q(course=self.course)).count()
        if self.payed():
            r = 'Yes'
        else:
            r = 'No'

        if c > 0:
            # this user didn't payed for other courses
            r += ', owes {} more'.format(c)
        return r

    get_payment_state.short_description = "Payed?"

    def mark_as_payed(self, payment_method, user=None):
        with transaction.atomic(), reversion.create_revision():
            self.state = Subscribe.State.PAYED
            self.paymentmethod = payment_method
            self.save()
            if user is not None:
                reversion.set_user(user)
            reversion.set_comment("Payed using payment method " + payment_method)
        if payment_method == PaymentMethod.ONLINE:
            send_online_payment_successful(self)
        return True

    def get_price_to_pay(self):
        if self.user.profile.student_status == 'no':
            return self.course.price_without_legi
        else:
            return self.course.price_with_legi

    # derives the matching state from the current information (if couple course and if partner set or not)
    def derive_matching_state(self):
        if self.course.type.couple_course:
            if self.partner is None:
                if self.matching_state not in [Subscribe.MatchingState.TO_MATCH, Subscribe.MatchingState.TO_REMATCH]:
                    self.matching_state = Subscribe.MatchingState.TO_MATCH
            else:
                if self.matching_state in [Subscribe.MatchingState.TO_MATCH, Subscribe.MatchingState.TO_REMATCH]:
                    self.matching_state = Subscribe.MatchingState.MATCHED
        else:
            self.matching_state = 'not_required'
            # DO NOT save here since this method is also called from save()

    def clean(self):
        # Don't allow subscriptions with partner equals to subscriber
        if self.partner == self.user:
            raise ValidationError('Subscriptions with yourself as the partner are not allowed.')

    def save(self, *args, **kwargs):
        self.derive_matching_state()
        super(Subscribe, self).save(*args, **kwargs)  # ensure id is set
        self.usi = self.generate_usi()
        super(Subscribe, self).save(*args, **kwargs)

    def __str__(self):
        return "{} subscribes to {}".format(self.user.get_full_name(), self.course)


class Confirmation(models.Model):
    subscription = models.ForeignKey(Subscribe, related_name='confirmations')
    date = models.DateField(blank=False, null=False, auto_now_add=True)
    date.help_text = "The date when the participation confirmation mail was sent to the subscriber."

    def __str__(self):
        return "({}) confirmed at {}".format(self.subscription, self.date)


class Rejection(models.Model):
    class Reason:
        UNKNOWN = 'unknown'
        OVERBOOKED = 'overbooked'
        NO_PARTNER = 'no_partner'
        USER_CANCELLED = 'user_cancelled'
        ILLEGITIMATE = 'illegitimate'
        BANNED = 'banned'
        COURSE_CANCELLED = 'course_cancelled'

        CHOICES = ((UNKNOWN, 'Unknown'), (OVERBOOKED, 'Overbooked'), (NO_PARTNER, 'No partner found'),
                   (USER_CANCELLED, 'User cancelled the subscription'),
                   (ILLEGITIMATE, 'Users subscription is illegitimate'), (BANNED, 'User is banned'),
                   (COURSE_CANCELLED, 'Course was cancelled'))

    subscription = models.ForeignKey(Subscribe, related_name='rejections')
    date = models.DateField(blank=False, null=False, auto_now_add=True)
    date.help_text = "The date when the rejection mail was sent to the subscriber."
    reason = models.CharField(max_length=30,
                              choices=Reason.CHOICES, blank=False, null=False,
                              default=Subscribe.MatchingState.UNKNOWN)
    mail_sent = models.BooleanField(blank=False, null=False, default=True)
    mail_sent.help_text = "If this rejection was communicated to user by email."

    def __str__(self):
        return "({}) rejected at {}".format(self.subscription, self.date)


# not a class method and therefore outside
def generate_key():
    voucher_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
    while Voucher.objects.filter(key=voucher_key).count() > 0:
        voucher_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return voucher_key


@reversion.register()
class Voucher(models.Model):
    purpose = models.ForeignKey('VoucherPurpose', related_name='vouchers')
    key = models.CharField(max_length=8, unique=True, default=generate_key)
    issued = models.DateField(blank=False, null=False, auto_now_add=True)
    expires = models.DateField(blank=True, null=True)
    used = models.BooleanField(blank=False, null=False, default=False)
    pdf_file = models.FileField(upload_to='/voucher/', null=True, blank=True)

    def mark_as_used(self, user=None, comment=""):
        with transaction.atomic(), reversion.create_revision():
            self.used = True
            self.save()
            if user is not None and not user.is_anonymous():
                reversion.set_user(user)
            reversion.set_comment("Marked as used. " + comment)
        return True

    class Meta:
        ordering = ['issued', 'expires']

    def __str__(self):
        return "#{} valid {} - {}".format(self.key, self.issued, self.expires)


class VoucherPurpose(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Teach(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='teaching')
    course = models.ForeignKey('Course', related_name='teaching')

    def __str__(self):
        return "{} teaches {}".format(self.teacher, self.course)


# An offering is a list of courses to be offered in the given period
class Offering(models.Model):
    class Type:
        REGULAR = 'reg'
        IRREGULAR = 'irr'

        CHOICES = ((REGULAR, 'Regular (weekly)'), (IRREGULAR, 'Irregular (Workshops)'))

    name = models.CharField(max_length=30, unique=True, blank=False)
    period = models.ForeignKey(Period, blank=True, null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=3,
                            choices=Type.CHOICES,
                            default=Type.REGULAR)
    type.help_text = "The type of the offering influences how the offering is displayed."
    display = models.BooleanField(default=False)
    display.help_text = "Defines if the courses in this offering should be displayed on the Website."
    active = models.BooleanField(default=False)
    active.help_text = "Defines if clients can subscribe to courses in this offering."

    def is_preview(self):
        return not self.display

    def __str__(self):
        return "{}".format(self.name)


class Song(models.Model):
    title = models.CharField(max_length=255, blank=False)
    artist = models.CharField(max_length=255, blank=True, null=True)
    length = models.TimeField(blank=True, null=True)
    speed = models.IntegerField(blank=True, null=True)
    speed.help_text = "The speed of the song in TPM"
    style = models.ForeignKey(Style, related_name='songs', blank=False, null=True, on_delete=models.SET_NULL)
    url_video = models.URLField(max_length=500, blank=True, null=True)
    url_video.help_text = "A url to a demo video (e.g Youtube)."

    def __str__(self):
        return "{} - {}".format(self.title, self.artist)

    class Meta:
        ordering = ['speed', 'length', ]
