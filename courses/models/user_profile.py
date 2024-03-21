import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, Iterable

from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.db.models import CASCADE, SET_NULL
from django.db.models import (
    Model,
    IntegerField,
    BooleanField,
    ImageField,
    DateField,
    DecimalField,
    OneToOneField,
    CharField,
)
from django.dispatch import receiver
from django_countries.data import COUNTRIES
from djangocms_text_ckeditor.fields import HTMLField

from courses import managers
from . import (
    Address,
    BankAccount,
    StudentStatus,
    Residence,
    Subscribe,
    CourseType,
    Course,
    Teach,
)


def upload_path(_, filename) -> str:
    extension = filename.split(".")[-1]
    return f"profile_pictures/{uuid.uuid4()}.{extension}"


class UserProfile(Model):
    user = OneToOneField(
        User, primary_key=True, related_name="profile", on_delete=CASCADE
    )
    user.help_text = "The user which is matched to this user profile."

    language = CharField(max_length=10, blank=False, default="en")

    legi = CharField(max_length=16, blank=True, null=True)
    gender = CharField(max_length=64, blank=True, null=True)
    address = OneToOneField(Address, blank=True, null=True, on_delete=SET_NULL)
    phone_number = CharField(max_length=255, blank=True, null=True)
    student_status = CharField(
        max_length=10,
        choices=StudentStatus.CHOICES,
        blank=False,
        null=False,
        default=StudentStatus.NO,
    )
    body_height = IntegerField(blank=True, null=True)
    body_height.help_text = "The user's body height in cm."
    newsletter = BooleanField(default=True)
    get_involved = BooleanField(default=False)
    get_involved.help_text = (
        "If this user is interested to get involved with our organisation."
    )

    picture = ImageField(null=True, blank=True, upload_to=upload_path)
    about_me = HTMLField(blank=True, null=True)

    birthdate = DateField(blank=True, null=True)
    nationality = CharField(
        max_length=2,
        choices=[("", "Select country")] + list(COUNTRIES.items()),
        blank=True,
        null=True,
    )
    residence_permit = CharField(
        max_length=30, choices=Residence.CHOICES, blank=True, null=True
    )
    ahv_number = CharField(max_length=255, blank=True, null=True)
    zemis_number = CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Every registered foreigner in switzerland gets a ZEMIS number.",
    )
    bank_account = OneToOneField(
        BankAccount,
        related_name="user_profile",
        blank=True,
        null=True,
        on_delete=SET_NULL,
    )
    fixed_hourly_wage = DecimalField(
        decimal_places=2,
        max_digits=6,
        blank=True,
        null=True,
        help_text="Only set this value if there is a special agreement.",
    )

    objects = managers.UserProfileManager()

    @staticmethod
    @receiver(user_logged_in)
    def set_language(**kwargs) -> None:
        user = kwargs["user"]
        lang_code = kwargs["request"].LANGUAGE_CODE
        try:
            user.profile.language = lang_code
            user.profile.save()
        except UserProfile.DoesNotExist:
            pass

    # convenience method for model user are added here
    def is_teacher(self) -> bool:
        return self.user.teaching_courses.count() > 0

    def is_student(self) -> bool:
        return self.student_status in StudentStatus.STUDENTS and self.legi

    # At least one course ends in the future
    def is_current_teacher(self) -> bool:
        for teaching in self.user.teaching_courses.all():
            last_date = teaching.course.get_last_lesson_date()
            if last_date is not None and last_date >= date.today():
                return True

        return False

    def teaching_since(self) -> Optional[date]:
        if not self.is_teacher():
            return None

        earliest_course = None
        for teaching in self.courses_taught():
            course_start = teaching.course.get_first_lesson_date()
            if not course_start:
                continue
            if (
                not earliest_course
                or course_start < earliest_course.get_first_lesson_date()
            ):
                earliest_course = teaching.course

        if earliest_course:
            return earliest_course.get_first_lesson_date()

    def courses_taught_count(self) -> int:
        return len(self.courses_taught())

    def total_hours_taught(self) -> Decimal:
        return sum(
            [teaching.course.get_total_hours() for teaching in self.courses_taught()],
            Decimal(0),
        )

    def courses_taught(self) -> set[Teach]:
        return {
            teaching
            for teaching in self.user.teaching_courses.all()
            if not teaching.course.is_external() and not teaching.course.cancelled
        }

    def is_board_member(self) -> bool:
        return self.user.functions.count() > 0

    def get_styles_of_teacher(self) -> set[CourseType]:
        if not self.is_teacher():
            return set()

        styles = set()
        for teaching in self.user.teaching_courses.all():
            styles.update(set(teaching.course.type.styles.all()))

        return styles

    def get_subscriptions(self) -> Iterable[Subscribe]:
        return self.user.subscriptions.order_by("-date").all()

    def subscriptions_with_overdue_payment(self) -> Iterable[Subscribe]:
        return [
            subscription
            for subscription in self.get_subscriptions()
            if subscription.is_payment_overdue()
        ]

    def get_subscribed_courses(self) -> Iterable[Course]:
        return [s.course for s in self.get_subscriptions()]

    def get_past_subscriptions(self) -> Iterable[Subscribe]:
        sql = (
            "SELECT * FROM courses_subscribe "
            "WHERE user_id = %s AND course_id IN (SELECT id FROM past_courses) "
            "ORDER BY id DESC"
        )
        return Subscribe.objects.raw(sql, [self.user_id])

    def get_current_teaching_courses(self) -> Iterable[Course]:
        courses = [
            t.course for t in self.user.teaching_courses.all() if not t.course.is_over()
        ]
        courses.sort(key=lambda c: c.get_first_lesson_date() or date.min)
        return courses

    def get_current_subscriptions(self) -> Iterable[Subscribe]:
        sql = (
            "SELECT * FROM courses_subscribe "
            "WHERE user_id = %s AND course_id IN (SELECT id FROM current_courses) "
            "ORDER BY id DESC"
        )
        return Subscribe.objects.raw(sql, [self.user_id])

    def get_student_status(self) -> str:
        return StudentStatus.TEXT[self.student_status]

    def get_residence_permit(self) -> str:
        return Residence.PERMITS[self.residence_permit]

    def get_nationality(self) -> str:
        return self.nationality.name

    def is_complete(self) -> bool:
        return not self.missing_values()

    def missing_values(self) -> Iterable[str]:
        if self.is_teacher():
            missing = []
            if not self.birthdate:
                missing.append("birth date")
            if not self.residence_permit:
                missing.append("residence permit")
            if not self.ahv_number:
                missing.append("AHV number")
            # Every registered foreigner in switzerland gets a ZEMIS number, thus applicable for everyone except swiss
            # and non-registered people (e.g. short term stay withoutt need for visa)
            if not self.zemis_number and self.residence_permit not in ["SWISS", "<NO>"]:
                missing.append("ZEMIS number")
            if not self.bank_account:
                missing.append("bank account")

            return missing
        return []

    class Meta:
        permissions = (("access_counterpayment", "Can access counter payment"),)

    def __str__(self) -> str:
        return "{}".format(self.user.get_full_name())
