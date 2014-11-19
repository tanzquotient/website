from django.conf.urls import patterns, url

from faq import views

urlpatterns = patterns('',
    url(r'^$', views.faq, name='home'),
    url(r'^faq/$', views.faq, name='faq'),
)