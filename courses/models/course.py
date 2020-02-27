import datetime

from django.conf import settings
from django.contrib import auth
from django.db import models
from djangocms_text_ckeditor.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFields

from courses import managers
from courses.models import PaymentMethod, Weekday, Gender, CourseSubscriptionType, MatchingState


class Course(TranslatableModel):
    # Mandatory fields
    name = models.CharField(max_length=255, blank=False)
    name.help_text = "This name is just for reference and is not displayed anywhere on the website."
    type = models.ForeignKey('CourseType', related_name='courses', blank=False, null=False, on_delete=models.PROTECT)
    type.help_text = "The name of the course type is displayed on the website as the course title ."
    subscription_type = models.CharField(max_length=20, blank=False, null=False,
                                         choices=CourseSubscriptionType.CHOICES,
                                         default=CourseSubscriptionType.REGULAR)
    display = models.BooleanField(default=True)
    display.help_text = "Defines if this course should be displayed on the Website " \
                        "(if checked, course is displayed if offering is displayed)."
    active = models.BooleanField(default=True)
    active.help_text = "Defines if clients can subscribe to this course " \
                       "(if checked, course is active if offering is active)."
    evaluated = models.BooleanField(default=False)
    evaluated.help_text = "If this course was evaluated by a survey or another way."

    # Optional - apply to all course types
    room = models.ForeignKey('Room', related_name='courses', blank=True, null=True, on_delete=models.PROTECT)
    offering = models.ForeignKey('Offering', blank=True, null=True, on_delete=models.PROTECT)
    offering.help_text = "Not required! Useful for regular courses or summer workshops. " \
                         "Do not use for irrgeular courses (e.g. ASVZ open classes)"
    period = models.ForeignKey('Period', blank=True, null=True, on_delete=models.PROTECT)
    period.help_text = "You can set a custom period for this course here. " \
                       "If this is left empty, the period from the offering is taken. " \
                       "Must be set if no offering associated but has regular lessons."

    # Translated fields
    translations = TranslatedFields(
        description=HTMLField(verbose_name='[TR] Description', blank=True, null=True,
                              help_text="Description specific for this course. "
                                        "(Gets displayed combined with the description of the course style)")
    )

    # For regular courses only
    min_subscribers = models.IntegerField(blank=True, null=True)
    max_subscribers = models.IntegerField(blank=True, null=True)

    # For external courses only
    external_url = models.URLField(max_length=500, blank=True, null=True)

    # Pricing
    price_with_legi = models.FloatField(blank=True, null=True, default=35)
    price_without_legi = models.FloatField(blank=True, null=True, default=70)
    price_special = models.CharField(max_length=255, blank=True, null=True)
    price_special.help_text = "Set this only if you want a different price schema."

    # Relations
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                         through='Subscribe',
                                         related_name='courses',
                                         through_fields=('course', 'user'))
    preceding_courses = models.ManyToManyField('Course',
                                               related_name='succeeding_courses',
                                               through='CourseSuccession',
                                               through_fields=('successor', 'predecessor'))
    preceding_courses.help_text = "The course(s) that are immediate predecessors of this course."

    objects = managers.CourseManager()

    def participatory(self):
        return self.subscriptions.accepted()

    def payment_totals(self):
        """calculate different statistics in one method (performance optimization)"""
        totals = {
            'to_pay': 0,
            'paid': 0,
            'unpaid': 0,
            'paid_count': 0,
            'not_paid_count': 0,
            'paid_course': 0,
            'paid_voucher': 0,
            'paid_online': 0,
            'paid_counter': 0,
        }
        accepted = self.subscriptions.accepted()
        for s in accepted.all():
            price = s.get_price_to_pay() or 0
            totals['to_pay'] += price

        paid = accepted.paid()
        totals['paid_count'] = paid.count()
        totals['not_paid_count'] = accepted.count() - paid.count()
        for s in paid.all():
            price = s.get_price_to_pay() or 0
            totals['paid'] += price
            if s.paymentmethod == PaymentMethod.ONLINE:
                totals['paid_online'] += price
            if s.paymentmethod == PaymentMethod.VOUCHER:
                totals['paid_voucher'] += price
            if s.paymentmethod == PaymentMethod.COURSE:
                totals['paid_course'] += price
            if s.paymentmethod == PaymentMethod.COUNTER:
                totals['paid_counter'] += price
        totals['unpaid'] = totals['to_pay'] - totals['paid']

        return totals

    def format_teachers(self):
        return ', '.join(map(auth.get_user_model().get_full_name, self.get_teachers()))

    def get_teachers(self):
        return [t.teacher for t in self.teaching.all()]

    format_teachers.short_description = "Teachers"

    def format_prices(self):
        from courses.services import format_prices
        return format_prices(self.price_with_legi, self.price_without_legi, self.price_special)

    format_prices.short_description = "Prices"

    def format_description(self):
        from courses.services import model_attribute_language_fallback
        desc = ""
        desc += model_attribute_language_fallback(self, 'description') or ""
        desc += model_attribute_language_fallback(self.type, 'description') or ""
        return desc

    format_description.short_description = "Description"

    def is_custom_period(self):
        return self.period is not None

    def get_period(self):
        if self.period is None:
            if self.offering:
                return self.offering.period
        else:
            return self.period
        return None

    def show_free_places_count(self):
        """ only show free_places_count if it can be calculated """
        counts = self.get_free_places_count()
        if counts is not None:
            return {
                'total': counts['total'] > 0,
                'man': counts['man'] > 0,
                'woman': counts['woman'] > 0
            }
        else:
            return None

    def has_free_places(self):
        counts = self.get_free_places_count()
        if counts is not None:
            return counts['total'] > 0 or counts['man'] > 0 or counts['woman'] > 0
        else:
            return True

    def get_free_places_count(self):
        """ Creates a dict with the free places totally and for men/women separately """
        if self.max_subscribers is not None:
            subscriptions = self.subscriptions.active()

            c = self.max_subscribers - subscriptions.count()
            if self.type.couple_course:
                matched_count = subscriptions.filter(matching_state__in=MatchingState.MATCHED_STATES).count()
                unmatched_male_count = subscriptions.filter(user__profile__gender=Gender.MEN, matching_state__in=MatchingState.TO_MATCH_STATES).count()
                unmatched_female_count = subscriptions.filter(user__profile__gender=Gender.WOMAN, matching_state__in=MatchingState.TO_MATCH_STATES).count()
                effective_max = (self.max_subscribers - matched_count) // 2
                cm = effective_max - unmatched_male_count
                cw = effective_max - unmatched_female_count
            else:
                cm = c
                cw = c
            c = int(max(c, 0))
            cm = int(max(cm, 0))
            cw = int(max(cw, 0))
            return {
                'total': c,
                'man': cm,
                'woman': cw
            }
        else:
            return None

    def get_confirmed_count(self):
        return self.subscriptions.accepted().count()

    def men_count(self):
        return self.subscriptions.active().men().count()

    def confirmed_men_count(self):
        return self.subscriptions.accepted().men().count()

    def confirmed_women_count(self):
        return self.subscriptions.accepted().women().count()

    def unconfirmed_men_count(self):
        return self.subscriptions.active().men().count() - self.subscriptions.accepted().men().count()

    def unconfirmed_women_count(self):
        return self.subscriptions.active().women().count() - self.subscriptions.accepted().women().count()

    def women_count(self):
        return self.subscriptions.active().women().count()

    def single_men_count(self):
        return self.subscriptions.active().single_men().count()

    def single_women_count(self):
        return self.subscriptions.active().single_women().count()

    def men_needed(self):
        return self.single_men_count() < self.single_women_count()

    def women_needed(self):
        return self.single_women_count() < self.single_men_count()

    def has_style(self, style_name):
        if style_name is None:
            return True

        for style in self.type.styles.all():
            if style.name == style_name:
                return True

            parent = style.parent_style
            while parent:
                if parent.name == style_name:
                    return True
                parent = parent.parent_style

        return False

    def is_displayed(self, preview=False):
        if self.offering is None:
            return self.display
        else:
            return preview or (self.offering.display and self.display)  # both must be true to be displayed

    def is_external(self):
        return self.subscription_type == CourseSubscriptionType.EXTERNAL

    def is_open_class(self):
        return self.subscription_type == CourseSubscriptionType.OPEN_CLASS

    def is_regular(self):
        return self.subscription_type == CourseSubscriptionType.REGULAR

    def subscription_opens_soon(self):
        period = self.get_period()
        if period is None or period.date_from is None:
            return False

        return self.subscription_closed() and period.date_from > datetime.date.today()

    def subscription_closed(self):
        return self.is_regular() and not self.is_subscription_allowed()

    def is_subscription_allowed(self):
        if not self.is_regular():
            return False

        if self.offering is None:
            return self.active

        return self.offering.active and self.active  # both must be true to allow subscription

    def is_over(self):
        last_date = self.get_last_lesson_date()
        if last_date:
            return last_date < datetime.date.today()
        if self.get_period() and self.get_period().date_to is not None:
            return self.get_period().date_to < datetime.date.today()
        return False

    def get_lessons(self):
        lessons = []
        lessons.extend(self.regular_lessons.all())
        lessons.extend(self.irregular_lessons.all())
        return lessons

    def get_all_regular_lesson_exceptions(self):
        exceptions = []
        for regular_lesson in self.regular_lessons.all():
            exceptions += [e for e in regular_lesson.exceptions.all() if e.is_applicable()]
        return exceptions

    def get_not_cancelled_regular_lesson_exceptions(self):
        return [e for e in self.get_all_regular_lesson_exceptions() if not e.is_cancellation]

    def get_lessons_as_strings(self):
        return map(str, self.get_lessons())

    def format_lessons(self):
        return ' & '.join(self.get_lessons_as_strings())

    format_lessons.short_description = "Lessons"

    def get_regular_lesson_cancellation_dates(self):
        def is_applicable(date):
            period = self.get_period()
            weekdays = [Weekday.NUMBERS[r.weekday] for r in self.regular_lessons.all()]

            return date.weekday() in weekdays and period.date_from <= date <= period.date_to

        return [d for d in self.get_cancellation_dates() if is_applicable(d)]

    def get_cancellation_dates(self):
        dates = []
        for regular_lesson in self.regular_lessons.all():
            for exception in regular_lesson.exceptions.all():
                if exception.is_cancellation:
                    dates.append(exception.date)

        period = self.get_period()
        if period:
            dates += [c.date for c in period.cancellations.all()]
        return sorted(dates)

    def format_cancellations(self):
        dates = [d.strftime('%d.%m.%Y') for d in self.get_cancellation_dates()]
        return ' / '.join(dates)

    format_cancellations.short_description = "Cancellations"

    def format_preceeding_courses(self):
        return ' / '.join(map(str, self.preceding_courses.all()))

    format_preceeding_courses.short_description = "Predecessors"

    def get_first_regular_lesson(self):
        if self.regular_lessons.exists():
            return self.regular_lessons.all()[0]
        else:
            return None

    def get_first_irregular_lesson(self):
        if self.irregular_lessons.exists():
            return self.irregular_lessons.all()[0]
        return None

    def get_last_irregular_lesson(self):
        if self.irregular_lessons.exists():
            return self.irregular_lessons.all()[0]
        return None

    @staticmethod
    def next_weekday(d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead < 0:  # Target day already happened
            days_ahead += 7
        return d + datetime.timedelta(days_ahead)

    def get_first_regular_lesson_date(self):
        lesson = self.get_first_regular_lesson()
        period = self.get_period()
        if lesson and period and period.date_from:
            return Course.next_weekday(period.date_from, lesson.get_weekday_number())
        else:
            return None

    def get_last_regular_lesson_date(self):
        period = self.get_period()
        if self.regular_lessons.exists() and period and period.date_to:
            course_weekdays = [Weekday.NUMBERS[lesson.weekday] for lesson in self.regular_lessons.all()]

            # Find last course day before date_to
            for day_delta in range(7):
                day = period.date_to - datetime.timedelta(days=day_delta)
                if day.weekday() in course_weekdays:
                    return day

        return None

    def get_first_irregular_lesson_date(self):
        lesson = self.get_first_irregular_lesson()
        return lesson.date if lesson else None

    def get_last_irregular_lesson_date(self):
        lesson = self.get_last_irregular_lesson()
        return lesson.date if lesson else None

    def get_first_lesson_date(self):
        d1 = self.get_first_irregular_lesson_date()
        d2 = self.get_first_regular_lesson_date()
        if d1 is None and d2 is None:
            return None
        if d1 is None:
            return d2
        if d2 is None:
            return d1

        return d1 if d1 < d2 else d2

    def get_last_lesson_date(self):
        d1 = self.get_last_irregular_lesson_date()
        d2 = self.get_last_regular_lesson_date()
        if d1 is None:
            return d2
        if d2 is None:
            return d1

        return d1 if d1 > d2 else d2

    def get_common_irregular_weekday(self):
        """Returns a weekday string if all irregular lessons are on same weekday, otherwise returns None"""
        if self.irregular_lessons.exists():
            weekdays = [lesson.date.weekday() for lesson in self.irregular_lessons.all()]
            weekdays_unique = list(set(weekdays))
            if len(weekdays_unique) == 1:
                return Weekday.NUMBER_2_SLUG[weekdays_unique[0]]
            else:
                return None
        else:
            return None

    def get_teachers_welcomed(self):
        return self.teaching.filter(welcomed=True).count() > 0

    get_teachers_welcomed.short_description = 'Teachers welcomed'
    get_teachers_welcomed.boolean = True

    def get_total_time(self):
        totals = {
            'total': None,
            'regular': None,
            'irregular': None,
        }
        regular_times = [l.get_total_time() for l in list(self.regular_lessons.all())]
        irregular_times = [l.get_total_time() for l in list(self.irregular_lessons.all())]
        if all(t is not None for t in regular_times):
            totals['regular'] = sum(t.seconds / 3600 for t in regular_times)
        if all(t is not None for t in irregular_times):
            totals['irregular'] = sum(t.seconds / 3600 for t in irregular_times)
        try:
            totals['total'] = totals['regular'] + totals['irregular']
        except TypeError:
            pass
        return totals

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

        # copy teachers
        for teach in old.teaching.all():
            teach.pk = None
            teach.welcomed = False
            teach.course = self
            teach.save()

        return self

    # position field for ordering columns (grappelli feature)
    position = models.PositiveSmallIntegerField('Position', default=0)

    class Meta:
        ordering = ['position', 'name']

    def __str__(self):
        return "{} ({})".format(self.name, self.offering)
