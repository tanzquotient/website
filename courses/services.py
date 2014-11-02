from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from django.contrib import messages

from django.contrib.auth.models import User
import models as mymodels

import logging
from django.utils import datastructures
log = logging.getLogger('courses')

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
    
    userinfo=get_or_create_userinfo(user)
    userinfo.legi=user_data['legi']
    userinfo.gender=user_data['gender']
    userinfo.address=mymodels.Address.objects.create_from_user_data(user_data)
    userinfo.phone_number=user_data['phone_number']
    userinfo.student_status=user_data['student_status']
    userinfo.newsletter=user_data['newsletter']
    userinfo.save()
    
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
    userinfo = mymodels.UserInfo(user=user,legi=user_data['legi'],gender=user_data['gender'],address=mymodels.Address.objects.create_from_user_data(user_data),phone_number=user_data['phone_number'],student_status=user_data['student_status'],newsletter=user_data['newsletter'])
    userinfo.user=user
    userinfo.save()
    return user    

def generate_username(first_name, last_name):
    username="{}_{}".format(first_name,last_name)
    un=username
    i=1;
    while User.objects.filter(username=un).count() > 0:
        un=username+str(i)
        i+=1
            
    return un.lower()
    
def subscribe(course_id, user1_data, user2_data=None):
    course = mymodels.Course.objects.get(id=course_id)
    user1 = get_or_create_user(user1_data)
    if user2_data:
        user2 = get_or_create_user(user2_data)
    else:
        user2=None
    
    subscription = mymodels.Subscribe(user=user1,course=course,partner=user2,experience=user1_data['experience'],comment=user1_data['comment'])
    subscription.save();
    
    if user2:
        subscription2 = mymodels.Subscribe(user=user2,course=course,partner=user1,experience=user2_data['experience'],comment=user2_data['comment'])
        subscription2.save()
        
def get_or_create_userinfo(user):
    try:
        return mymodels.UserInfo.objects.get(user=user)
    except ObjectDoesNotExist:
        userinfo = mymodels.UserInfo(user=user)
        return userinfo

# finds a list of courses the 'user' did already and that are somehow relevant for 'course'
def calculate_relevant_experience(user,course):
    relevant_exp = [style.id for style in course.type.styles.all()]
    return [s.course for s in mymodels.Subscribe.objects.filter(user=user,course__type__styles__id__in=relevant_exp).order_by('course__type__level').all() if s.course != course]
