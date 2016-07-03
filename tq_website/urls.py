from django.conf.urls import include, url
from django.http import HttpResponse
from django.contrib import admin

from django.conf.urls.i18n import i18n_patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from . import views
import django.views.i18n
import views
import courses.views as courses_views
import rest_framework.urls
import userena.urls
import survey.urls
import payment.urls
import cms.urls

urlpatterns = [
    # url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")), # comment out robots or change it when site is finished
    url(r'^jsi18n/(?P<packages>\S+?)/$', django.views.i18n.javascript_catalog),
    url(r'^export/newsletter/$', views.newsletter_list, name="newsletter_list"),
    url(r'^export/no-newsletter/$', views.no_newsletter_list, name="no_newsletter_list"),
    url(r'^check/$', courses_views.confirmation_check, name='confirmation_check'),
    url(r'^duplicate-users/$', courses_views.duplicate_users, name="duplicate_users"),
    url(r'^api-auth/', include(rest_framework.urls, namespace='rest_framework'))
]

# for testing error pages
if settings.DEBUG:
    urlpatterns += [url(r'^400/$', TemplateView.as_view(template_name='400.html')),
                    url(r'^403/$', TemplateView.as_view(template_name='403.html')),
                    url(r'^404/$', TemplateView.as_view(template_name='404.html')),
                    url(r'^500/$', TemplateView.as_view(template_name='500.html')),
                    ]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    # Examples:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include(userena.urls)),
    url(r'^survey/', include(survey.urls, namespace='survey')),
    url(r'^', include(payment.urls, namespace='payment')),
    url(r'^', include(cms.urls))
)
