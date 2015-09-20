#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.db import models

import datetime
from django.utils.translation import ugettext as _

from django.conf import settings

import django.contrib.auth as auth

import managers
from django.core.exceptions import ValidationError
from courses.services import calculate_relevant_experience, format_prices
from djangocms_text_ckeditor.fields import HTMLField

from django.db.models import Q

WEEKDAYS = (('mon', u'Monday'), ('tue', u'Tuesday'), ('wed', u'Wednesday'),
            ('thu', u'Thursday'), ('fri', u'Friday'), ('sat', u'Saturday'),
            ('sun', u'Sunday'))

WEEKDAYS_TRANS = {'mon': u'Montag', 'tue': u'Dienstag', 'wed': 'Mittwoch', 'thu': 'Donnerstag', 'fri': 'Freitag',
                  'sat': 'Samstag', 'sun': 'Sonntag'}

OFFERING_TYPES = (('reg', u'Regular (weekly)'), ('irr', u'Irregular (Workshops)'),)

LEVELS = ((1, u'beginner'), (2, u'intermediate'), (3, u'advanced'))

GENDER = (('m', u'Men'), ('w', u'Woman'))

STUDENT_STATUS = (('eth', u'ETH'), ('uni', u'Uni'), ('ph', u'PH'), ('other', u'Other'), ('no', u'Not a student'))

MATCHING_STATE = (('unknown', u'Unknown'), ('couple', u'Couple'), ('to_match', u'To match'), ('matched', u'Matched'), ('not_required', u'Not required'))

REJECTION_REASON = (('unknown', u'Unknown'), ('overbooked', u'Overbooked'), ('no_partner', u'No partner found'))

class Address(models.Model):
    street = models.CharField(max_length=255)
    plz = models.IntegerField()
    city = models.CharField(max_length=255)

    objects = managers.AddressManager()

    def equals(self, a):
        return self.street == a.street and self.plz == a.plz and self.city == a.city

    def __unicode__(self):
        return u"{}, {} {}".format(self.street, self.plz, self.city)

from userena.models import UserenaLanguageBaseProfile

class UserProfile(UserenaLanguageBaseProfile):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name='profile')
    user.help_text = "The user which is matched to this user profile."
    legi = models.CharField(max_length=16, blank=True, null=True)
    gender = models.CharField(max_length=1,
                              choices=GENDER, blank=False, null=True,
                              default=None)
    address = models.ForeignKey(Address, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    student_status = models.CharField(max_length=10,
                                      choices=STUDENT_STATUS, blank=False, null=False,
                                      default='no')
    body_height = models.IntegerField(blank=True, null=True)
    body_height.help_text = "The user's body height in cm."
    newsletter = models.BooleanField(default=True)
    get_involved = models.BooleanField(default=False)
    get_involved.help_text = "If this user is interested to get involved with our organisation."

    about_me = HTMLField(blank=True, null=True)

    def __unicode__(self):
        return u"{}".format(self.user.get_full_name())


class Style(models.Model):
    name = models.CharField(max_length=30, unique=True, blank=False)
    description = HTMLField(blank=True, null=True)
    url_info = models.URLField(max_length=500, blank=True, null=True)
    url_info.help_text = "A url to an information page (e.g. Wikipedia)."
    url_video = models.URLField(max_length=500, blank=True, null=True)
    url_video.help_text = "A url to a demo video (e.g Youtube)."

    def __unicode__(self):
        return u"{}".format(self.name)


class Room(models.Model):
    name = models.CharField(max_length=30, unique=True, blank=False)
    description = HTMLField(blank=True, null=True)
    address = models.OneToOneField(Address, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    url.help_text = "The url to Google Maps (see https://support.google.com/maps/answer/144361?p=newmaps_shorturl&rd=1)"
    contact_info = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u"{}".format(self.name)


class Period(models.Model):
    date_from = models.DateField(blank=True, null=True)
    date_from.help_text = u"The start date of this period. Can be left empty."
    date_to = models.DateField(blank=True, null=True)
    date_to.help_text = u"The end date of this period. Can be left empty. If both are left empty, this period is displayed as 'on request'."

    def format_date(self, d):
        return d.strftime('%d. %b %Y')

    format_date.short_description = 'Period from/to'

    def __unicode__(self):
        if self.date_from and self.date_to:
            return u"{} - {}".format(self.format_date(self.date_from), self.format_date(self.date_to))
        elif self.date_from:
            return u"ab {}".format(self.format_date(self.date_from))
        elif self.date_to:
            return u"bis {}".format(self.format_date(self.date_to))
        else:
            return u"ganzjährlich"


class RegularLesson(models.Model):
    course = models.ForeignKey('Course', related_name='regular_lessons')
    weekday = models.CharField(max_length=3,
                               choices=WEEKDAYS,
                               default=None)
    time_from = models.TimeField()
    time_to = models.TimeField()

    def __unicode__(self):
        return u"{}, {}-{}".format(WEEKDAYS_TRANS[self.weekday], self.time_from.strftime("%H:%M"),
                                   self.time_to.strftime("%H:%M"))


class RegularLessonCancellation(models.Model):
    course = models.ForeignKey('Course', related_name='cancellations')
    date = models.DateField(blank=False, null=True)

    class Meta:
        ordering = ['date']

    def __unicode__(self):
        return u"{}".format(self.date.strftime('%d.%m.%Y'))


class IrregularLesson(models.Model):
    course = models.ForeignKey('Course', related_name='irregular_lessons')
    date = models.DateField(blank=False, null=False)
    time_from = models.TimeField()
    time_to = models.TimeField()
    room = models.ForeignKey(Room, related_name='irregular_lessons', blank=True, null=True, on_delete=models.SET_NULL)
    room.help_text = "The room for this lesson. If left empty, the course room is assumed."

    class Meta:
        ordering = ['date', 'time_from']

    def __unicode__(self):
        s = u"{}, {}-{}".format(self.date, self.time_from.strftime("%H:%M"),
                                self.time_to.strftime("%H:%M"))
        if self.room:
            s = s + u", {}".format(self.room)
        return s


class CourseType(models.Model):
    name = models.CharField(max_length=30, unique=True, blank=False)
    styles = models.ManyToManyField(Style, related_name='course_types', blank=True, null=True)
    level = models.IntegerField(default=None, blank=True, null=True)
    description = HTMLField(blank=True, null=True)
    couple_course = models.BooleanField(default=True)

    def get_level(self):
        return self.level if self.level else "";

    def format_styles(self):
        return ', '.join(map(str, self.styles.all()))

    format_styles.short_description = "Styles"

    def __unicode__(self):
        return u"{}".format(self.name)


class PeriodCancellation(models.Model):
    course = models.ForeignKey('Period', related_name='cancellations')
    date = models.DateField(blank=False, null=True)

    def __unicode__(self):
        return u"{}".format(self.date.strftime('%d.%m.%Y'))


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
    price_special.help_text = u"Set this only if you want a different price schema."
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

    objects = managers.CourseManager()

    def format_teachers(self):
        return ', '.join(map(auth.get_user_model().get_full_name, self.teachers.all()))

    format_teachers.short_description = "Teachers"

    def format_prices(self):
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
            c = self.max_subscribers - self.subscriptions.filter(confirmed=True).count()
            if c > 0:
                return c
            else:
                return 0
        else:
            return None

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

    def is_displayed(self):
        if self.offering is None:
            return False
        else:
            return self.offering.display and self.display  # both must be true to be displayed

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
        return u' & '.join(self.get_lessons_as_strings())

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
        return u' / '.join(dates)

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

    def get_first_lesson_date(self):
        fil = self.get_first_irregular_lesson()
        d1 = None
        d2 = None
        if fil is not None:
            d1 = fil.date
        if self.get_period() is not None:
            d2 = self.get_period().date_from
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
        ordering = ['position']

    def __unicode__(self):
        return u"{} ({})".format(self.name, self.offering)


class Subscribe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subscriptions')
    course = models.ForeignKey(Course, related_name='subscriptions')
    date = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    date.help_text = "The date/time when the subscription was made."
    partner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subscriptions_as_partner', blank=True,
                                null=True)
    matching_state = models.CharField(max_length=30,
                                      choices=MATCHING_STATE, blank=False, null=False,
                                      default='unknown')
    experience = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    comment.help_text = "A optional comment made by the user during subscription."
    confirmed = models.BooleanField(blank=False, null=False, default=False)
    confirmed.help_text = "When this is checked, a participation confirmation email is send (once) to the user while saving this form."
    rejected = models.BooleanField(blank=False, null=False, default=False)
    rejected.help_text = "When this is checked, a rejection email is send (once) to the user while saving this form."
    payed = models.BooleanField(blank=False, null=False, default=False)

    objects = managers.SubscribeManager()

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
        return ', '.join(map(str, calculate_relevant_experience(self.user, self.course)))

    get_calculated_experience.short_description = "Calculated experience"

    # returns similar courses that the user did before in the system
    def get_payment_status(self):
        c = self.user.subscriptions.filter(payed=False, course__offering__active=False, confirmed=True).filter(
            ~Q(course=self.course)).count()
        if self.payed:
            r = 'Yes'
        else:
            r = 'No'

        if c > 0:
            # this user didn't payed for other courses
            r += ', owes {} more'.format(c)
        return r

        return ', '.join(map(str, calculate_relevant_experience(self.user, self.course)))

    get_payment_status.short_description = "Payed?"

    def get_price_to_pay(self):
        if self.user.profile.student_status == 'no':
            return self.course.price_without_legi
        else:
            return self.course.price_with_legi

    # derives the matching state from the current information (if couple course and if partner set or not)
    def derive_matching_state(self):
        if self.course.type.couple_course:
            if self.partner is None:
                self.matching_state='to_match'
            else:
                if self.matching_state=='to_match':
                    self.matching_state='matched'
        else:
            self.matching_state='not_required'
        # DO NOT save here since this method is also called from save()

    def clean(self):
        # Don't allow subscriptions with partner equals to subscriber
        if self.partner == self.user:
            raise ValidationError('Subscriptions with yourself as the partner are not allowed.')

    def save(self, *args, **kwargs):
        self.derive_matching_state()
        super(Subscribe, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"{} subscribes to {}".format(self.user.get_full_name(), self.course)


class Confirmation(models.Model):
    subscription = models.ForeignKey(Subscribe, related_name='confirmations')
    date = models.DateField(blank=False, null=False, auto_now_add=True)
    date.help_text = "The date when the participation confirmation mail was sent to the subscriber."

    def __unicode__(self):
        return u"({}) confirmed at {}".format(self.subscription, self.date)


class Rejection(models.Model):
    subscription = models.ForeignKey(Subscribe, related_name='rejections')
    date = models.DateField(blank=False, null=False, auto_now_add=True)
    date.help_text = "The date when the rejection mail was sent to the subscriber."
    reason = models.CharField(max_length=30,
                                      choices=REJECTION_REASON, blank=False, null=False,
                                      default='unknown')

    def __unicode__(self):
        return u"({}) rejected at {}".format(self.subscription, self.date)


class Teach(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='teaching')
    course = models.ForeignKey('Course', related_name='teaching')

    def __unicode__(self):
        return u"{} teaches {}".format(self.teacher, self.course)


# An offering is a list of courses to be offered in the given period
class Offering(models.Model):
    name = models.CharField(max_length=30, unique=True, blank=False)
    period = models.ForeignKey(Period, blank=True, null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=3,
                            choices=OFFERING_TYPES,
                            default='reg')
    type.help_text = "The type of the offering influences how the offering is displayed."
    display = models.BooleanField(default=False)
    display.help_text = "Defines if the courses in this offering should be displayed on the Website."
    active = models.BooleanField(default=False)
    active.help_text = "Defines if clients can subscribe to courses in this offering."

    def format_period(self):
        return self.period

    def __unicode__(self):
        return u"{}".format(self.name)


class Song(models.Model):
    title = models.CharField(max_length=255, blank=False)
    artist = models.CharField(max_length=255, blank=True, null=True)
    length = models.TimeField(blank=True, null=True)
    speed = models.IntegerField(blank=True, null=True)
    speed.help_text = "The speed of the song in TPM"
    style = models.ForeignKey(Style, related_name='songs', blank=False, null=True, on_delete=models.SET_NULL)
    url_video = models.URLField(max_length=500, blank=True, null=True)
    url_video.help_text = "A url to a demo video (e.g Youtube)."

    def __unicode__(self):
        return u"{} - {}".format(self.title, self.artist)

    class Meta:
        ordering = ['speed', 'length', ]
