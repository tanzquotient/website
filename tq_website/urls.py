import cms.urls
import django.views.i18n
import photologue.urls
import rest_framework.urls
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.views.generic import TemplateView

import courses.urls
import courses.views as courses_views
import email_system.urls
import events.urls
import payment.urls
import survey.urls

urlpatterns = [
    path("jsi18n/<packages>/", django.views.i18n.JavaScriptCatalog.as_view()),
    path("check/", courses_views.confirmation_check, name="confirmation_check"),
    path("duplicate-users/", courses_views.duplicate_users, name="duplicate_users"),
    path("api-auth/", include(rest_framework.urls, namespace="rest_framework")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

# for testing error pages
if settings.DEBUG:
    urlpatterns += [
        path("400/", TemplateView.as_view(template_name="400.html")),
        path("403/", TemplateView.as_view(template_name="403.html")),
        path("404/", TemplateView.as_view(template_name="404.html")),
        path("500/", TemplateView.as_view(template_name="500.html")),
    ]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("password/", courses_views.change_password, name="change_password"),
    path("profile/courses", courses_views.user_courses, name="user_courses"),
    path("profile/<int:user_id>/calendar.ical", courses_views.user_ical, name="user_ical"),
    path("profile/edit", courses_views.ProfileView.as_view(), name="edit_profile"),
    path("profile/", courses_views.user_profile, name="profile"),
    path("survey/", include(survey.urls, namespace="survey")),
    path("events/", include(events.urls, namespace="events")),
    path("courses/", include(courses.urls, namespace="courses")),
    path("emails/", include(email_system.urls, namespace="email_system")),
    path("photos/", include(photologue.urls, namespace="photos")),
    path("hijack/", include("hijack.urls")),
    path("", include(payment.urls, namespace="payment")),
    path("", include(cms.urls)),
)
