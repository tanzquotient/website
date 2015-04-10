from django.conf.urls import patterns, url, include

from courses import views

urlpatterns = patterns('',
    url(r'^$', views.course_list, name='home'),
    url(r'^list/$', views.course_list, name='list'),
    url(r'^detail/(?P<course_id>\d+)/$', views.subscription, name='subscription'),
    url(r'^detail/(?P<course_id>\d+)/second$', views.subscription2, name='subscription2'),
    url(r'^detail/(?P<course_id>\d+)/subscription$', views.subscription_do, name='subscription_do'),
    url(r'^detail/(?P<course_id>\d+)/subscription_done$', views.subscription_done, name='subscription_done'),
)