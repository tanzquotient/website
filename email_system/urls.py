from django.conf.urls import url
from email_system.apps import EmailSystemConfig

from email_system import views

app_name = EmailSystemConfig.name
urlpatterns = [
    url(r'^unsubscribe/(?P<context>[\w\s0-9_-]+)/(?P<user_id>\d+)/(?P<code>[\w-]+)/$', views.unsubscribe, name='unsubscribe'),
]
