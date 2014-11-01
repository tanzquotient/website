from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from django.contrib import messages

from django.contrib.auth.models import User
from models import *

import logging
log = logging.getLogger('courses')

# Create your services here.

def get_offering_to_display():
    offerings= Offering.objects.filter(period__date_from__lte=datetime.date.today()).order_by('period__date_from')
    # return offering starting earliest or None if no offering
    if len(offerings)>0:
        return offerings[0]
    else:
        return None

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
    
    #address = Address({k: user_data[k] for k in ('street', 'plz', 'city')})
    #address.save()
    
    userinfo=get_or_create_userinfo(user)
    userinfo.legi=user_data['legi']
    userinfo.gender=user_data['gender']
    userinfo.address=None
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
    #address = Address({k: user_data[k] for k in ('street', 'plz', 'city')})
    #address.save()
    userinfo = UserInfo(user=user,legi=user_data['legi'],gender=user_data['gender'],address=None,phone_number=user_data['phone_number'],student_status=user_data['student_status'],newsletter=user_data['newsletter'])
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
            
    return un
    
def subscribe(course_id, user1_data, user2_data=None):
    course = Course.objects.get(id=course_id)
    user1 = get_or_create_user(user1_data)
    if user2_data:
        user2 = get_or_create_user(user2_data)
    else:
        user2=None
    
    subscription = Subscribe(user=user1,course=course,partner=user2,experience=user1_data['experience'],comment=user1_data['comment'])
    subscription.save();
    
    if user2:
        subscription2 = Subscribe(user=user2,course=course,partner=user1,experience=user2_data['experience'],comment=user2_data['comment'])
        subscription2.save()
        
def get_or_create_userinfo(user):
    try:
        return UserInfo.objects.get(user=user).first()
    except ObjectDoesNotExist:
        userinfo = UserInfo(user=user)
        return userinfo
