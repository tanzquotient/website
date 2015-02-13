#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from django.contrib import messages

from django.contrib.auth.models import User
import models as mymodels

import logging
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
    userprofile.phone_number=user_data['phone_number']
    userprofile.student_status=user_data['student_status']
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
    userprofile = mymodels.UserProfile(user=user,legi=user_data['legi'],gender=user_data['gender'],address=mymodels.Address.objects.create_from_user_data(user_data),phone_number=user_data['phone_number'],student_status=user_data['student_status'],newsletter=user_data['newsletter'])
    userprofile.user=user
    userprofile.save()
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

def confirm_subscription(subscription):
    if subscription.confirmed and mymodels.Confirmation.objects.filter(subscription=subscription).count() == 0:
        # no subscription was send and the subscription is confirmed, so send one
        if send_participation_confirmation(subscription):
            # log that we sent the confirmation
            c = mymodels.Confirmation(subscription=subscription)
            c.save()

        
def get_or_create_userprofile(user):
    try:
        return mymodels.UserProfile.objects.get(user=user)
    except ObjectDoesNotExist:
        userprofile = mymodels.UserProfile(user=user)
        return userprofile

# finds a list of courses the 'user' did already and that are somehow relevant for 'course'
def calculate_relevant_experience(user,course):
    relevant_exp = [style.id for style in course.type.styles.all()]
    return [s.course for s in mymodels.Subscribe.objects.filter(user=user,course__type__styles__id__in=relevant_exp).order_by('course__type__level').all() if s.course != course]

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
