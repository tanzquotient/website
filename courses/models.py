from django.db import models

import datetime
from django.utils.translation import ugettext as _


from django.conf import settings

import django.contrib.auth as auth

import managers

WEEKDAYS = (('mon', u'Monday'), ('tue', u'Tuesday'), ('wed', u'Wednesday'),
               ('thu', u'Thursday'), ('fri', u'Friday'), ('sat', u'Saturday'),
               ('sun', u'Sunday'))

LEVELS = ((1, u'beginner'),(2,u'intermediate'),(3,u'advanced'))

GENDER = (('m', u'Men'), ('w', u'Woman'))

STUDENT_STATUS = (('eth', u'ETH'), ('uni', u'Uni'), ('ph', u'PH'), ('other', u'Other'), ('no', u'Not a student'))
            
class Address(models.Model):
    street = models.CharField(max_length=30)
    plz = models.IntegerField()
    city = models.CharField(max_length=30)
    
    def __unicode__(self):
        return u"{} {}, {} {}".format(self.street,self.number,self.plz,self.city)

class UserInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    user.help_text="The user profile which is matched to this user info."
    legi = models.CharField(max_length=16, blank=True, null=True)
    gender = models.CharField(max_length=1,
                                      choices=GENDER, blank=False, null=False,
                                      default=None)
    address = models.OneToOneField(Address, blank=True, null=True)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    student_status = models.CharField(max_length=3,
                                      choices=STUDENT_STATUS, blank=False, null=False,
                                      default=None)
    newsletter = models.BooleanField(default=True)
    
    def __unicode__(self):
        return u"{}".format(self.user.get_full_name())
    
    
class Style(models.Model):
    name = models.CharField(max_length=30, unique=True, blank=False)
    description = models.TextField(blank=True, null=True)
    url_info = models.URLField(blank=True, null=True)
    url_info.help_text="A url to an information page (e.g. Wikipedia)."
    url_video = models.URLField(blank=True, null=True)
    url_video.help_text="A url to a demo video (e.g Youtube)."
    
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)
    
    def __unicode__(self):
        return u"{}".format(self.name)
    
class Room(models.Model):
    name = models.CharField(max_length=30, unique=True, blank=False)
    description = models.TextField(blank=True, null=True)
    address = models.OneToOneField(Address, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    contact_info = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return u"{}".format(self.name)

class Period(models.Model):
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    
    def format_date(self,d):
        return d.strftime('%d. %b %Y')
    format_date.short_description = 'Period from/to'
    
    def __unicode__(self):
        return u"{} - {}".format(self.format_date(self.date_from), self.format_date(self.date_to))

class CourseTime(models.Model):
    list_display = ('course', 'weekday', 'time_from', 'time_to', )

    course = models.ForeignKey('Course', related_name='times')
    weekday = models.CharField(max_length=3,
                                      choices=WEEKDAYS,
                                      default=None)
    time_from = models.TimeField()
    time_to = models.TimeField()
    
    def __unicode__(self):
        return u"{}, {}-{}".format(_(self.weekday),self.time_from.strftime("%H:%M") ,self.time_to.strftime("%H:%M") )

class CourseType(models.Model):
    list_display = ('name', 'styles', 'level', 'couple_course',)

    name = models.CharField(max_length=30, unique=True, blank=False)
    styles = models.ManyToManyField(Style, related_name='course_types', blank=True, null=True)
    level = models.CharField(max_length=3,
                                      choices=LEVELS,
                                      default=None, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    spezial = models.TextField(blank=True, null=True)
    couple_course = models.BooleanField(default=True)
    
    def get_level(self):
        return _(self.level)
        
    def format_styles(self):
        return ', '.join(map(str,self.styles.all()))
    format_styles.short_description="Styles"
    
    def __unicode__(self):
        return u"{}".format(self.name)

class PeriodCancellation(models.Model):
    course = models.ForeignKey('Period', related_name='cancellations')
    date = models.DateField(blank=False, null=True)
    
class CourseCancellation(models.Model):
    course = models.ForeignKey('Course', related_name='cancellations')
    date = models.DateField(blank=False, null=True)
    
class Course(models.Model):
    list_display = ('name', 'offering', 'period', 'room', )

    name = models.CharField(max_length=30, blank=False)
    name.help_text = "This name is just for reference and is not displayed anywhere on the website."
    type = models.ForeignKey(CourseType,related_name='courses', blank=False, null=False)
    type.help_text = "The name of the course type is displayed on the website as the course title ."
    room = models.ForeignKey(Room, related_name='courses', blank=True, null=True)
    min_subscribers = models.IntegerField(blank=False,null=False,default=6)
    max_subscribers = models.IntegerField(blank=True,null=True)
    price_with_legi = models.FloatField(blank=True, null=True, default=35)
    price_without_legi = models.FloatField(blank=True, null=True, default=70)
    comment = models.TextField(blank=True, null=True)
    period = models.ForeignKey(Period,blank=True, null=True)
    period.help_text="You can set a custom period for this course here. If this is left empty, the period from the offering is taken."
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Teach', related_name='teaching_courses')
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Subscribe', related_name='courses', through_fields=('course','user'))
    offering = models.ForeignKey('Offering')
    
    objects=managers.CourseManager()
    
    def format_teachers(self):
        return ', '.join(map(auth.get_user_model().get_full_name,self.teachers.all()))
    format_teachers.short_description="Teachers"
    
    def format_prices(self):
        r = self.price_with_legi.__str__()+u" / "+self.price_without_legi.__str__()+" CHF"
        return r
    format_prices.short_description="Prices"
    
    def get_period(self):
        if(self.period is None):
            return self.offering.period
        else:
            return self.period
        
    def get_free_places_count(self):
        if self.max_subscribers != None:
            return self.max_subscribers-self.subscribers.count()
        else:
            return None
        
    def is_subscription_allowed(self):
        return self.offering.active
    
    def format_times(self):
        return u' / '.join(map(str,self.times.all()))
    format_times.short_description="Times"
    
    def get_first_time(self):
        if self.times.exists():
            return self.times.all()[0]
        else:
            return None
    
    # position field for ordering columns (grappelli feature)
    position = models.PositiveSmallIntegerField("Position", default=0)
    class Meta:
        ordering = ['position']
    
    # autocomplete fields (grappelli feature)
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)
          
    def __unicode__(self):
        return u"{}".format(self.name)

class Subscribe(models.Model):
    list_display = ('user', 'course', 'partner', 'payed', 'confirmed')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subscriptions')
    course = models.ForeignKey(Course, related_name='subscriptions')
    date = models.DateField(blank=False, null=False, auto_now_add=True)
    date.help_text="The date when the subscription was made."
    partner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subscriptions_as_partner', blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    comment.help_text="A optional comment made by the user during subscription."
    payed = models.BooleanField(blank=False, null=False, default=False)
    confirmed = models.BooleanField(blank=False, null=False, default=False)
    confirmed.help_text="When this is checked, a confirmation email is send (once) to the user while saving this form."

    def __unicode__(self):
        return u"{} subscribes to {}".format(self.user.get_full_name(),self.course)
    
class Teach(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='teaching')
    course = models.ForeignKey('Course', related_name='teaching')
    
    def __unicode__(self):
        return u"{} teaches {}".format(self.teacher,self.course)

# An offering is a list of courses to be offered in the given period
class Offering(models.Model):
    list_display = ('name', 'active')
    
    name = models.CharField(max_length=30, unique=True, blank=False)
    period = models.ForeignKey(Period,blank=True, null=True)
    display = models.BooleanField(default=False)
    display.help_text="Defines if the courses in this offering should be displayed on the Website."
    active = models.BooleanField(default=False)
    active.help_text="Defines if clients can subscribe to courses in this offering."
    
    def format_period(self):
        return self.period
        
    # autocomplete fields (grappelli feature)
    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)
    
    def __unicode__(self):
        return u"{}".format(self.name)
