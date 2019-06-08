from django.conf import settings
from django.db import models
from django_countries.fields import CountryField
from djangocms_text_ckeditor.fields import HTMLField

from courses import managers
from . import Address, BankAccount, Gender, StudentStatus, Residence


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name='profile')
    user.help_text = "The user which is matched to this user profile."
    legi = models.CharField(max_length=16, blank=True, null=True)
    gender = models.CharField(max_length=1,
                              choices=Gender.CHOICES, blank=False, null=True,
                              default=None)
    address = models.ForeignKey(Address, blank=True, null=True, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    student_status = models.CharField(max_length=10,
                                      choices=StudentStatus.CHOICES, blank=False, null=False,
                                      default=StudentStatus.NO)
    body_height = models.IntegerField(blank=True, null=True)
    body_height.help_text = "The user's body height in cm."
    newsletter = models.BooleanField(default=True)
    get_involved = models.BooleanField(default=False)
    get_involved.help_text = "If this user is interested to get involved with our organisation."

    picture = models.ImageField(null=True, blank=True)
    about_me = HTMLField(blank=True, null=True)

    birthdate = models.DateField(blank=True, null=True)
    nationality = CountryField(blank=True, null=True)
    residence_permit = models.CharField(max_length=30, choices=Residence.CHOICES, blank=True, null=True)
    ahv_number = models.CharField(max_length=255, blank=True, null=True)
    bank_account = models.OneToOneField(BankAccount, blank=True, null=True, on_delete=models.CASCADE)
    default_hourly_wage = models.FloatField(default=30.0)
    default_hourly_wage.help_text = "The default hourly wage, which serves as a preset value for taught courses. "

    objects = managers.UserProfileManager()

    # convenience method for model user are added here
    def is_teacher(self):
        return self.user.teaching.count() > 0

    def teaching_since(self):
        if not self.is_teacher():
            return None

        earliest_course = None
        for teaching in self.user.teaching.all():
            course_start = teaching.course.get_first_lesson_date()
            if not course_start:
                continue
            if not earliest_course or course_start < earliest_course.get_first_lesson_date():
                earliest_course = teaching.course

        if earliest_course:
            return earliest_course.get_first_lesson_date()

    def teacher_courses_count(self):
        if not self.is_teacher():
            return 0

        return self.user.teaching.count()

    def is_board_member(self):
        return self.user.functions.count() > 0

    def get_styles_of_teacher(self):
        if not self.is_teacher():
            return []

        styles = set()
        for teaching in self.user.teaching.all():
            styles.update(set(teaching.course.type.styles.all()))

        return styles

    def get_student_status(self):
        return StudentStatus.TEXT[self.student_status]

    def get_residence_permit(self):
        return Residence.PERMITS[self.residence_permit]

    def get_nationality(self):
        return self.nationality.name

    def is_complete(self):
        return not self.missing_values()

    def missing_values(self):
        if self.is_teacher():
            missing = []
            if not self.birthdate:
                missing.append('birth date')
            if not self.residence_permit:
                missing.append('residence permit')
            if not self.ahv_number:
                missing.append('AHV number')
            if not self.bank_account:
                missing.append('bank account')

            return missing
        return []

    class Meta:
        permissions = (
            ("access_counterpayment", "Can access counter payment"),
        )

    def __str__(self):
        return "{}".format(self.user.get_full_name())
