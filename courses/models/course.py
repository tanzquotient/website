from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta, datetime
from decimal import Decimal
from numbers import Number
from typing import Optional, Union, Iterable

from django.conf import settings
from django.contrib import auth, admin
from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFields

from courses import managers
from courses.models import (
    Weekday,
    CourseSubscriptionType,
    LeadFollow,
    Subscribe,
    Period,
    RegularLesson,
    IrregularLesson,
    RegularLessonException,
    LessonOccurrence,
)
from partners.models import Partner
from survey.models import Survey
from utils.helpers import optional_min, optional_max


class Course(TranslatableModel):
    # Mandatory fields
    offering = models.ForeignKey("Offering", on_delete=models.PROTECT)
    name = models.CharField(max_length=255, blank=False)
    name.help_text = (
        "This name is just for reference and is not displayed anywhere on the website."
    )
    type = models.ForeignKey(
        "CourseType",
        related_name="courses",
        blank=False,
        null=False,
        on_delete=models.PROTECT,
    )
    type.help_text = (
        "The name of the course type is displayed on the website as the course title ."
    )
    subscription_type = models.CharField(
        max_length=20,
        blank=False,
        null=False,
        choices=CourseSubscriptionType.CHOICES,
        default=CourseSubscriptionType.REGULAR,
    )
    display = models.BooleanField(default=True)
    display.help_text = (
        "Defines if this course should be displayed on the Website "
        "(if checked, course is displayed if offering is displayed)."
    )
    active = models.BooleanField(default=True)
    active.help_text = (
        "Defines if clients can subscribe to this course "
        "(if checked, course is active if offering is active)."
    )
    cancelled = models.BooleanField(
        default=False, help_text="Indicates if this course is cancelled"
    )
    experience_mandatory = models.BooleanField(
        default=False,
        help_text="If enabled, people registering for this course need to state their "
        "experience.",
    )

    # Optional - apply to all course types
    room = models.ForeignKey(
        "Room", related_name="courses", blank=True, null=True, on_delete=models.PROTECT
    )
    period = models.ForeignKey(
        "Period", blank=True, null=True, on_delete=models.PROTECT
    )
    period.help_text = (
        "You can set a custom period for this course here. "
        "If this is left empty, the period from the offering is taken. "
    )

    # Translated fields
    translations = TranslatedFields(
        description=HTMLField(
            verbose_name="[TR] Description",
            blank=True,
            null=True,
            help_text="Description specific for this course. "
            "(Gets displayed combined with the description of the course style)",
        ),
        information_for_participants_teachers=HTMLField(
            verbose_name="[TR] Information for participants (editable by teachers)",
            blank=True,
            null=True,
            help_text=_(
                "Shown only to participants of the course on the course page. Can be set by teachers in the frontend."
            ),
        ),
    )

    # For regular courses only
    min_subscribers = models.IntegerField(blank=True, null=True)
    max_subscribers = models.IntegerField(blank=True, null=True)

    # For external courses only
    external_url = models.URLField(max_length=500, blank=True, null=True)
    partner = models.ForeignKey(
        to=Partner,
        on_delete=models.SET_NULL,
        related_name="courses",
        blank=True,
        null=True,
    )

    # Pricing
    price_with_legi = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6, default=Decimal(35)
    )
    price_without_legi = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6, default=Decimal(70)
    )
    price_special = models.CharField(max_length=255, blank=True, null=True)
    price_special.help_text = "Set this only if you want a different price schema."

    # Relations
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Subscribe",
        related_name="courses",
        through_fields=("course", "user"),
    )
    preceding_courses = models.ManyToManyField(
        "Course",
        related_name="succeeding_courses",
        through="CourseSuccession",
        through_fields=("successor", "predecessor"),
    )
    preceding_courses.help_text = (
        "The course(s) that are immediate predecessors of this course."
    )

    objects = managers.CourseManager()

    def participatory(self) -> QuerySet[Subscribe]:
        return self.subscriptions.accepted()

    def participants(self) -> set[User]:
        return {subscription.user for subscription in self.subscriptions.accepted()}

    def subscribed_user_ids(self) -> set[int]:
        return {
            subscription.user_id
            for subscription in self.subscriptions.all()
            if subscription.is_active()
        }

    def payment_totals(self) -> dict[str, Number]:
        """calculate different statistics in one method (performance optimization)"""
        totals = defaultdict(Decimal)
        accepted = self.subscriptions.accepted().prefetch_related(
            "price_reductions", "subscription_payments"
        )

        for subscription in accepted.all():
            totals["to_pay"] += subscription.get_price_to_pay()
            totals["paid"] += subscription.sum_of_payments()
            totals["reductions"] += subscription.sum_of_reductions()
            totals["to_pay_after_reductions"] += subscription.price_after_reductions()
            totals["open_amount"] += subscription.open_amount()

        totals["difference"] = totals["to_pay_after_reductions"] - totals["paid"]

        return totals

    def format_teachers(self) -> str:
        names = list(map(auth.get_user_model().get_full_name, self.get_teachers()))
        if not names:
            return ""
        if len(names) == 1:
            return names[0]
        return " & ".join([", ".join(names[:-1]), names[-1]])

    def get_teachers(self) -> list[User]:
        return [t.teacher for t in self.teaching.all()]

    def surveys(self) -> set[Survey]:
        return {
            survey_instance.survey for survey_instance in self.survey_instances.all()
        }

    format_teachers.short_description = "Teachers"

    def get_teacher_ids(self) -> set[int]:
        return {t.teacher_id for t in self.teaching.all()}

    def format_prices(self) -> str:
        from courses.services import format_prices

        return format_prices(
            self.price_with_legi, self.price_without_legi, self.price_special
        )

    format_prices.short_description = "Prices"

    def get_period(self) -> Period:
        return self.period or self.offering.period

    def show_free_places_count(self) -> bool:
        return self.max_subscribers is not None

    def has_free_places(self) -> bool:
        return self.max_subscribers is None or self.get_free_places_count() > 0

    def has_free_places_for_leaders(self) -> bool:
        return self.has_free_places_for(LeadFollow.LEAD)

    def has_free_places_for_followers(self) -> bool:
        return self.has_free_places_for(LeadFollow.FOLLOW)

    def has_free_places_for(self, lead_or_follow) -> bool:
        if self.max_subscribers is None:
            return True

        free_places = self.get_free_places_count()
        if free_places == 0:
            return False

        matched_count = self.matched_subscriptions_count()
        total_for_preference = (self.max_subscribers - matched_count) / 2
        current_count_for_preference = self.single_subscriptions_with_preference_count(
            lead_or_follow
        )
        free_for_preference = total_for_preference - current_count_for_preference

        return free_for_preference >= 1

    def active_subscriptions_count(self) -> int:
        return len(
            {
                subscription
                for subscription in self.subscriptions.all()
                if subscription.is_active()
            }
        )

    def matched_subscriptions_count(self) -> int:
        return len(
            {
                subscription
                for subscription in self.subscriptions.all()
                if subscription.is_matched()
            }
        )

    def single_subscriptions_with_preference_count(self, lead_or_follow) -> int:
        return len(
            {
                s
                for s in self.subscriptions.all()
                if s.is_single_with_preference(lead_or_follow)
            }
        )

    def get_free_places_count(self) -> Optional[int]:
        # No maximum => free places is not defined
        if self.max_subscribers is None:
            return None

        total_count = self.max_subscribers - self.active_subscriptions_count()
        total_count = int(max(total_count, 0))

        return total_count

    def get_confirmed_count(self) -> int:
        return self.subscriptions.accepted().count()

    def get_matched_and_individual_counts(self) -> tuple[int, int, int, int]:
        matched_count = self.matched_subscriptions_count()
        leads_count = self.single_subscriptions_with_preference_count(LeadFollow.LEAD)
        follows_count = self.single_subscriptions_with_preference_count(
            LeadFollow.FOLLOW
        )
        no_preference_count = self.single_subscriptions_with_preference_count(
            LeadFollow.NO_PREFERENCE
        )

        return matched_count, leads_count, follows_count, no_preference_count

    def number_of_possible_couples(self) -> int:
        (
            matched_count,
            leads_count,
            follows_count,
            no_preference_count,
        ) = self.get_matched_and_individual_counts()

        smaller_set_size = min(leads_count, follows_count)
        larger_set_size = max(leads_count, follows_count)

        diff = larger_set_size - smaller_set_size

        if no_preference_count <= diff:
            return matched_count // 2 + smaller_set_size + no_preference_count

        remaining = no_preference_count - diff
        return matched_count // 2 + larger_set_size + remaining // 2

    def min_number_of_couples(self) -> int:
        return (self.min_subscribers + 1) // 2  # round up

    def has_enough_participants(self) -> bool:
        if self.min_subscribers is None:
            return True  # If there is no minimum number of subscribers, we always have enough participants

        if self.type.couple_course:
            return self.number_of_possible_couples() >= self.min_number_of_couples()

        return self.active_subscriptions_count() >= self.min_subscribers

    def participants_info_title(self) -> str:
        if self.active_subscriptions_count() == 0:
            return _("We did not receive any subscriptions yet.")

        if self.type.couple_course:
            (
                matched_count,
                leads_count,
                follows_count,
                no_preference_count,
            ) = self.get_matched_and_individual_counts()
            if (
                matched_count // 2 + leads_count + follows_count + no_preference_count
                == 1
            ):
                return _("Currently there is:")
            return _("Currently there are:")

        count = self.active_subscriptions_count()
        if count == 1:
            return _("We received one subscription so far.")
        return _("We received {} subscriptions so far.").format(count)

    def participants_info_list(self) -> list[str]:
        if not self.type.couple_course:
            return []

        (
            matched_count,
            leads_count,
            follows_count,
            no_preference_count,
        ) = self.get_matched_and_individual_counts()
        texts = []
        if matched_count:
            texts.append(
                _("One couple")
                if matched_count // 2 == 1
                else _("{} couples").format(matched_count // 2)
            )
        if follows_count:
            texts.append(
                _("One individual follower")
                if follows_count == 1
                else _("{} individual followers").format(follows_count)
            )
        if leads_count:
            texts.append(
                _("One individual leader")
                if leads_count == 1
                else _("{} individual leaders").format(leads_count)
            )
        if no_preference_count:
            texts.append(
                _("One person with no lead or follow preference")
                if no_preference_count == 1
                else _("{} people with no lead or follow preference").format(
                    no_preference_count
                )
            )
        return texts

    def not_enough_participants_info(self) -> Optional[str]:
        if self.has_enough_participants():
            return None

        if self.type.couple_course:
            (
                matched_count,
                leads_count,
                follows_count,
                no_preference_count,
            ) = self.get_matched_and_individual_counts()

            if leads_count + follows_count + no_preference_count > 0:
                num_couples = self.number_of_possible_couples()
                if num_couples == 1:
                    return _(
                        "With this one couple is possible in total, but at least {} couples are needed."
                    ).format(self.min_number_of_couples())
                return _(
                    "With this {} couples are possible in total, but at least {} couples are needed."
                ).format(num_couples, self.min_number_of_couples())

            return _("At least {} couples are needed.").format(
                self.min_number_of_couples()
            )

        people_needed = self.min_subscribers - self.active_subscriptions_count()
        if people_needed == 1:
            return _("At least one more person is needed")
        return _("At least {} more people are needed.").format(people_needed)

    def has_style(self, style_name) -> bool:
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

    @admin.display(description="D", boolean=True)
    def is_displayed(self) -> bool:
        return (
            self.offering.display and self.display
        )  # both must be true to be displayed

    @admin.display(description="A", boolean=True)
    def is_active(self) -> bool:
        return self.offering.active and self.active

    def is_external(self) -> bool:
        return self.subscription_type == CourseSubscriptionType.EXTERNAL

    def is_open_class(self) -> bool:
        return self.subscription_type == CourseSubscriptionType.OPEN_CLASS

    def is_regular(self) -> bool:
        return self.subscription_type == CourseSubscriptionType.REGULAR

    def subscription_closed(self) -> bool:
        return self.is_regular() and not self.is_subscription_allowed()

    def is_subscription_allowed(self) -> bool:
        if not self.is_regular():
            return False

        return self.is_active()

    def is_over(self) -> bool:
        last_date = self.get_last_lesson_date() or self.get_period().date_to
        return last_date < date.today()

    def has_started_for(self, extra_time: timedelta = timedelta(days=7)) -> bool:
        return self.get_first_lesson_date() + extra_time < date.today()

    def get_lessons(self) -> list[Union[RegularLesson, IrregularLesson]]:
        return list(self.regular_lessons.all()) + list(self.irregular_lessons.all())

    def get_lesson_occurrences(self) -> Iterable[LessonOccurrence]:
        return [
            occurrence
            for lesson in self.get_lessons()
            for occurrence in lesson.get_occurrences()
        ]

    def get_regular_lesson_occurrences(self) -> Iterable[LessonOccurrence]:
        return [
            occurrence
            for lesson in self.regular_lessons.all()
            for occurrence in lesson.get_occurrences()
        ]

    def get_all_regular_lesson_exceptions(self) -> list[RegularLessonException]:
        exceptions = []
        for regular_lesson in self.regular_lessons.all():
            exceptions += [
                e for e in regular_lesson.exceptions.all() if e.is_applicable()
            ]
        return exceptions

    def get_not_cancelled_regular_lesson_exceptions(
        self,
    ) -> list[RegularLessonException]:
        return [
            e for e in self.get_all_regular_lesson_exceptions() if not e.is_cancellation
        ]

    def get_lessons_as_strings(self) -> Iterable[str]:
        return map(str, self.get_lessons())

    def format_lessons(self) -> str:
        return " & ".join(self.get_lessons_as_strings())

    def get_regular_lesson_cancellation_dates(self) -> list[date]:
        def is_applicable(cancelled_date) -> bool:
            weekdays = [Weekday.NUMBERS[r.weekday] for r in self.regular_lessons.all()]
            if cancelled_date.weekday() not in weekdays:
                return False

            period = self.get_period()
            return period.date_from <= cancelled_date <= period.date_to

        return [d for d in self.get_cancellation_dates() if is_applicable(d)]

    def get_cancellation_dates(self) -> list[date]:
        dates = []
        for regular_lesson in self.regular_lessons.all():
            for exception in regular_lesson.exceptions.all():
                if exception.is_cancellation:
                    dates.append(exception.date)

        dates += [c.date for c in self.get_period().cancellations.all()]
        return sorted(dates)

    def format_cancellations(self) -> str:
        dates = [d.strftime("%d.%m.%Y") for d in self.get_cancellation_dates()]
        return " / ".join(dates)

    format_cancellations.short_description = "Cancellations"

    def format_preceeding_courses(self) -> str:
        return " / ".join(map(str, self.preceding_courses.all()))

    format_preceeding_courses.short_description = "Predecessors"

    def get_first_regular_lesson(self) -> Optional[RegularLesson]:
        if self.regular_lessons.exists():
            return self.regular_lessons.all()[0]
        else:
            return None

    def get_first_lesson_start(self) -> Optional[datetime]:
        first = optional_min(self.get_lesson_occurrences())
        return first.start if first else None

    def get_first_lesson_date(self) -> Optional[date]:
        start = self.get_first_lesson_start()
        return start.date() if start else None

    def get_last_lesson_end(self) -> Optional[datetime]:
        last = optional_max(self.get_lesson_occurrences())
        return last.end if last else None

    def get_last_lesson_date(self) -> Optional[date]:
        end = self.get_last_lesson_end()
        return end.date() if end else None

    def get_first_regular_lesson_start(self) -> Optional[datetime]:
        first = optional_min(self.get_regular_lesson_occurrences())
        return first.start if first else None

    def get_first_regular_lesson_date(self) -> Optional[date]:
        start = self.get_first_regular_lesson_start()
        return start.date() if start else None

    def get_last_regular_lesson_end(self) -> Optional[datetime]:
        last = optional_max(self.get_regular_lesson_occurrences())
        return last.end if last else None

    def get_last_regular_lesson_date(self) -> Optional[date]:
        end = self.get_last_regular_lesson_end()
        return end.date() if end else None

    def get_common_irregular_weekday(self) -> Optional[str]:
        """Returns a weekday string if all irregular lessons are on same weekday, otherwise returns None"""
        if self.irregular_lessons.exists():
            weekdays = [
                lesson.date.weekday() for lesson in self.irregular_lessons.all()
            ]
            weekdays_unique = list(set(weekdays))
            if len(weekdays_unique) == 1:
                return Weekday.NUMBER_2_SLUG[weekdays_unique[0]]
            else:
                return None
        else:
            return None

    def get_teachers_welcomed(self) -> bool:
        return self.teaching.filter(welcomed=True).count() > 0

    get_teachers_welcomed.short_description = "Teachers welcomed"
    get_teachers_welcomed.boolean = True

    def get_total_time(self) -> timedelta:
        return sum(
            [lesson.get_total_time() for lesson in self.get_lessons()], timedelta()
        )

    def get_total_hours(self) -> Decimal:
        hour = timedelta(hours=1)
        return Decimal(
            f"{self.get_total_time().total_seconds() / hour.total_seconds():.2f}"
        )

    # create and stores identical copy of this course
    def copy(self) -> Course:
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
            teach.hourly_wage = None
            teach.save()

        return self

    class Meta:
        ordering = ["offering", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.offering})"
