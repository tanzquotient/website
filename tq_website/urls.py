from django.conf.urls import patterns, include, url
from django.http import HttpResponse
from django.contrib import admin

from django.conf.urls.i18n import i18n_patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
import views
import courses.views as courses_views

urlpatterns = patterns('',
                       # url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")), # comment out robots or change it when site is finished
                       url(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
                       url(r'^export/newsletter/$', views.newsletter_list, name="newsletter_list"),
                       url(r'^export/no-newsletter/$', views.no_newsletter_list, name="no_newsletter_list"),
                       url(r'^check/$', courses_views.confirmation_check, name='confirmation_check'),
                       url(r'^duplicate-users/$', courses_views.duplicate_users, name="duplicate_users"),
                       )

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns('',
                             # Examples:
                             url(r'^admin/', include(admin.site.urls)),
                             url(r'^accounts/', include('userena.urls')),
                             url(r'^', include('cms.urls')),

                             )
