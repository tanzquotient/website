from django.conf.urls import url

from email_system import views

app_name = 'events'
urlpatterns = [
    url(r'^unsubscribe/(?P<context>\w+)/(?P<user_id>\d+)/(?P<code>[\w-]+)/$', views.unsubscribe, name='unsubscribe'),
]
