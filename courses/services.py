#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from django.contrib import messages

from django.contrib.auth.models import User
import models as mymodels

import logging
from django.http.response import HttpResponse
log = logging.getLogger('courses')

from emailcenter import *

# Create your services here.

def get_offerings_to_display():
    # return offerings that have display flag on and order them with increasing start
    return mymodels.Offering.objects.filter(display=True).order_by('period__date_from')

def get_or_create_user(user_data):
    user = find_user(user_data)
    if user:
        return update_user(user, user_data)
    else:
        return create_user(user_data)

def update_user(user, user_data):
    fn = user_data['first_name']
    ln = user_data['last_name']
    
    user.email=user_data['email']
    user.first_name=fn
    user.last_name=ln
    user.save()
    
    userprofile=get_or_create_userprofile(user)
    userprofile.legi=user_data['legi']
    userprofile.gender= user_data['gender']
    userprofile.address=mymodels.Address.objects.create_from_user_data(user_data)
    if user_data['phone_number']:
        userprofile.phone_number=user_data['phone_number']
    userprofile.student_status=user_data['student_status']
    if user_data['body_height']:
        userprofile.body_height=user_data['body_height']
    userprofile.newsletter=user_data['newsletter']
    userprofile.save()
    
    return user
    
def find_user(user_data):
    # check if user already exists
    fn = user_data['first_name']
    ln = user_data['last_name']
    
    qs=User.objects.filter(first_name=fn,last_name=ln,email=user_data['email'])
    if len(qs)==1:
        return qs[0]
    else:
        return None
    
def create_user(user_data):
    fn = user_data['first_name']
    ln = user_data['last_name']
    
    user = User.objects.create_user(generate_username(fn, ln), email=user_data['email'], password=User.objects.make_random_password(), first_name=fn, last_name=ln)
    update_user(user, user_data)
    return user    

def generate_username(first_name, last_name):
    username=u"{}_{}".format(first_name,last_name)
    un=username
    i=1;
    while User.objects.filter(username=un).count() > 0:
        un=username+str(i)
        i+=1
            
    return un.lower()

def subscribe(course_id, user1_data, user2_data=None):
    res = dict()
    
    course = mymodels.Course.objects.get(id=course_id)
    user1 = get_or_create_user(user1_data)
    if user2_data:
        user2 = get_or_create_user(user2_data)
    else:
        user2=None
    
    if user1 == user2:
        res['tag'] = 'danger'
        res['text'] = u'Du kannst dich nicht mit dir selbst anmelden!'
    elif mymodels.Subscribe.objects.filter(user=user1, course__id=course_id).count() > 0:
        res['tag'] = 'danger'
        res['text'] = u'Du ({}) bist schon für diesen Kurs angemeldet!'.format(user1.first_name)
        res['long_text'] = u'Wenn du ein Fehler bei der Anmeldung gemacht hast, wende dich an tanzen@tq.vseth.ch'
    elif user2!=None and mymodels.Subscribe.objects.filter(user=user2, course__id=course_id).count() > 0:
        res['tag'] = 'danger'
        res['text'] = u'Dein Partner {} ist schon für diesen Kurs angemeldet!'.format(user2.first_name)
        res['long_text'] = u'Wenn du ein Fehler bei der Anmeldung gemacht hast, wende dich an tanzen@tq.vseth.ch'
    else:
        subscription = mymodels.Subscribe(user=user1,course=course,partner=user2,experience=user1_data['experience'],comment=user1_data['comment'])
        subscription.save();
        send_subscription_confirmation(subscription)
        
        if user2:
            subscription2 = mymodels.Subscribe(user=user2,course=course,partner=user1,experience=user2_data['experience'],comment=user2_data['comment'])
            subscription2.save()
            send_subscription_confirmation(subscription2)
            
        res['tag'] = 'info'
        res['text'] = u'Anmeldung erfolgreich.'
        res['long_text'] = u'Du erhältst in Kürze eine Emailbestätigung.'
        
    return res

# matches partners within the same course, considering their subscription time (fairness!)
def match_partners(subscriptions):
    courses=subscriptions.values_list('course', flat=True)
    log.info(courses)
    for course_id in courses:
        single = subscriptions.filter(course__id=course_id, partner__isnull=True).all()
        sm = single.filter(user__profile__gender='m').order_by('date').all()
        sw = single.filter(user__profile__gender='w').order_by('date').all()
        log.info(len(sm))
        log.info(len(sw))
        c = min(sm.count(), sw.count())
        while c>0:
            c=c-1
            m=sm[c]
            w=sw[c]
            m.partner=w.user
            m.save()
            w.partner=m.user
            w.save()

# sends a confirmation mail if subscription is confirmed (by some other method) and no confirmation mail was sent before
def confirm_subscription(subscription):
    if subscription.confirmed and mymodels.Confirmation.objects.filter(subscription=subscription).count() == 0:
        # no subscription was send and the subscription is confirmed, so send one
        send_participation_confirmation(subscription)
        # log that we sent the confirmation
        c = mymodels.Confirmation(subscription=subscription)
        c.save()

# same as confirm_subscription, but for multiple subscriptions at once
def confirm_subscriptions(subscriptions):
    for subscription in subscriptions:
        confirm_subscription(subscription)

        
def get_or_create_userprofile(user):
    try:
        return mymodels.UserProfile.objects.get(user=user)
    except ObjectDoesNotExist:
        userprofile = mymodels.UserProfile(user=user)
        return userprofile

# finds a list of courses the 'user' did already and that are somehow relevant for 'course'
def calculate_relevant_experience(user,course):
    relevant_exp = [style.id for style in course.type.styles.all()]
    return [s.course for s in mymodels.Subscribe.objects.filter(user=user,course__type__styles__id__in=relevant_exp).exclude(course=course).order_by('course__type__level').all()]

def format_prices(price_with_legi, price_without_legi):
    if price_with_legi and price_without_legi:
        if price_with_legi == price_without_legi:
            r = u"{} CHF".format(price_with_legi.__str__())
        else:
            r = u"mit Legi {} / sonst {} CHF".format(price_with_legi.__str__(), price_without_legi.__str__())
    elif price_without_legi:
        r = u"mit Legi freier Eintritt (sonst {} CHF)".format(price_without_legi.__str__())
    else:
        r = None # handle this case in template!
    return r


from auditing.models import Problem

def audit_user_error(user, tag, message):
    p = Problem(tag=tag, message = message, priority=Problem.PRIORITY_NORMAL, content_object=user)
    p.save()
    
import zipfile
import unicodecsv
from StringIO import StringIO

import openpyxl
from openpyxl.cell import get_column_letter
from openpyxl.styles import Alignment

# exports the subscriptions of course with course_id to fileobj (e.g. a HttpResponse)
def export_subscriptions(course_ids, export_format):
    def create_xlsx_sheet(wb, course_id, course_name):
        ws = wb.create_sheet(title=course_name)
    
        row_num = 0
    
        columns = [
            (u"Vorname", 20),
            (u"Nachname", 20),
            (u"Geschlecht", 10),
            (u"E-Mail", 50),
            (u"Mobile", 30),
            (u"Zu bezahlen", 10),
            (u"Erfahrung", 60),
        ]
    
        for col_num in xrange(len(columns)):
            c = ws.cell(row=row_num + 1, column=col_num + 1)
            c.value = columns[col_num][0]
            c.style = c.style.copy(font=c.style.font.copy(bold=True))
            # set column width
            ws.column_dimensions[get_column_letter(col_num+1)].width = columns[col_num][1]
    
        for s in mymodels.Subscribe.objects.filter(course__id=course_id, confirmed=True).order_by('user__first_name'):
            row_num += 1
            row = [s.user.first_name, s.user.last_name, s.user.profile.gender, s.user.email, s.user.profile.phone_number, s.get_price_to_pay(), s.experience]
            for col_num in xrange(len(row)):
                c = ws.cell(row=row_num + 1, column=col_num + 1)
                c.value = row[col_num]

                alignment = Alignment(wrap_text=True)
                c.style = c.style.copy(alignment=alignment)
                
    if len(course_ids)==1:
        course_id = course_ids[0]
        course_name = mymodels.Course.objects.get(id=course_id).name
        filename = u'Kursteilnehmer-{}'.format(course_name)
        if export_format=='csv':
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = u'attachment; filename="{}.csv"'.format(filename)
            
            writer = unicodecsv.writer(response)
            
            writer.writerow(['Vorname', 'Nachname', 'Geschlecht', 'E-Mail', 'Mobile','Zu bezahlen', 'Erfahrung'])
            for s in mymodels.Subscribe.objects.filter(course__id=course_id, confirmed=True).order_by('user__first_name'):
                row = [s.user.first_name, s.user.last_name, s.user.profile.gender, s.user.email, s.user.profile.phone_number, s.get_price_to_pay(), s.experience]
                writer.writerow(row)
        
            return response
        elif export_format=='xlsx':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = u'attachment; filename={}.xlsx'.format(filename)
            wb = openpyxl.Workbook()
            # remove preinitialized sheet
            wb.remove_sheet(wb.get_active_sheet())
            
            create_xlsx_sheet(wb, course_id, course_name)
            
            wb.save(response)
            return response
        else:
            return None
    elif len(course_ids) > 1:
        if export_format=='csv':
            zipped_file = StringIO()
            with zipfile.ZipFile(zipped_file, 'w') as f:
                for course_id in course_ids:
                    fileobj = StringIO()
                    writer = unicodecsv.writer(fileobj, encoding='utf-8')
            
                    writer.writerow(['Vorname', 'Nachname', 'Geschlecht', 'E-Mail', 'Mobile', 'Zu bezahlen', 'Erfahrung'])
                    for s in mymodels.Subscribe.objects.filter(course__id=course_id, confirmed=True).order_by('user__first_name'):
                        l = [s.user.first_name, s.user.last_name, s.user.profile.gender, s.user.email, s.user.profile.phone_number, s.get_price_to_pay(), s.experience]
                        writer.writerow(l)
                    f.writestr(u'Kursteilnehmer/{}.csv'.format(mymodels.Course.objects.get(id=course_id).name), fileobj.getvalue())
                    fileobj.seek(0)
                    
            
            zipped_file.seek(0)
            response = HttpResponse(zipped_file, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=Kursteilnehmer.zip'
            response['Content-Length'] = zipped_file.tell()
            
            return response
        elif export_format=='xlsx':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = u'attachment; filename=Kursteilnehmer.xlsx'
            wb = openpyxl.Workbook()
            # remove preinitialized sheet
            wb.remove_sheet(wb.get_active_sheet())
            
            for course_id in course_ids:
                create_xlsx_sheet(wb, course_id, mymodels.Course.objects.get(id=course_id).name)
            
            wb.save(response)
            return response
        else:
            return None
    else:
        return None
