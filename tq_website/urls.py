import cms.urls
import django.views.i18n
import rest_framework.urls
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

import courses.urls
import courses.views as courses_views
import email_system.urls
import events.urls
import payment.urls
import survey.urls

urlpatterns = [
    # url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")), # comment out robots or change it when site is finished
    url(r'^jsi18n/(?P<packages>\S+?)/$', django.views.i18n.JavaScriptCatalog.as_view()),
    url(r'^check/$', courses_views.confirmation_check, name='confirmation_check'),
    url(r'^duplicate-users/$', courses_views.duplicate_users, name="duplicate_users"),
    url(r'^api-auth/', include(rest_framework.urls, namespace='rest_framework')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
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
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^password/$', courses_views.change_password, name='change_password'),
    url(r'^profile/dashboard$', courses_views.user_dashboard, name='user_dashboard'),
    url(r'^profile/edit$', courses_views.ProfileView.as_view(), name='edit_profile'),
    url(r'^profile/$', courses_views.user_profile, name='profile'),
    url(r'^survey/', include(survey.urls, namespace='survey')),
    url(r'^events/', include(events.urls, namespace='events')),
    url(r'^courses/', include(courses.urls, namespace='courses')),
    url(r'^emails/', include(email_system.urls, namespace='email_system')),
    url(r'^', include(payment.urls, namespace='payment')),
    url(r'^', include(cms.urls))
)
