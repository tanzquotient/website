from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from tq_website import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tq.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^courses/', include('courses.urls', namespace="courses")),
    url(r'^$', views.home, name='home'),
    url(r'^home/$', views.home, name='home'),
    url(r'^events/$', views.events, name='events'),
    url(r'^gallery/$', views.gallery, name='gallery'),
    url(r'^faq/', include('faq.urls', namespace='faq')),
    url(r'^about/', include('organisation.urls', namespace='organisation')),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name="logout"),
)
