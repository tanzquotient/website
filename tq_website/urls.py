import cms.urls
import django.views.i18n
import photologue.urls
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.views.generic import TemplateView
from photologue.views import GalleryListView

import courses.urls
import courses.views as courses_views
import email_system.urls
import events.urls
import payment.urls
import survey.urls
from .views import WellKnownRedirectView, oidc_login_view, oidc_callback_view

urlpatterns = [
    path("jsi18n/<packages>/", django.views.i18n.JavaScriptCatalog.as_view()),
    path("check/", courses_views.confirmation_check, name="confirmation_check"),
    path("duplicate-users/", courses_views.duplicate_users, name="duplicate_users"),
]

if settings.DEBUG and not settings.TESTING:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()

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

# Make the ".well-known" static directory accessible via the root of the page
urlpatterns += [
    path(".well-known/<path:path>", WellKnownRedirectView.as_view()),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path(
        "accounts/new_login",
        TemplateView.as_view(template_name="account/new_login.html"),
        name="new_login",
    ),
    path("accounts/", include("allauth.urls")),
    path("password/", courses_views.change_password, name="change_password"),
    path("profile/courses", courses_views.user_courses, name="user_courses"),
    path(
        "profile/<int:user_id>/calendar.ical", courses_views.user_ical, name="user_ical"
    ),
    path("profile/edit", courses_views.ProfileView.as_view(), name="edit_profile"),
    path("profile/auth/oidc_login", oidc_login_view, name="oidc_login"),
    path("profile/auth/oidc_callback", oidc_callback_view, name="oidc_callback"),
    path("profile/", courses_views.user_profile, name="profile"),
    path("survey/", include(survey.urls, namespace="survey")),
    path("events/", include(events.urls, namespace="events")),
    path("courses/", include(courses.urls, namespace="courses")),
    path("emails/", include(email_system.urls, namespace="email_system")),
    path("photos/gallery/", GalleryListView.as_view(paginate_by=5), name="photos"),
    path("photos/", include(photologue.urls, namespace="photos")),
    path("hijack/", include("hijack.urls")),
    path("", include(payment.urls, namespace="payment")),
    path("", include(cms.urls)),
)
