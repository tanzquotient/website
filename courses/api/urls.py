from django.conf.urls import include
from django.urls import path

from .api import (
    UserDetail,
    CoursePaymentDetail,
    OfferingList,
    OfferingDetail,
    SubscriptionPayment,
    FilteredEmailList,
    CourseTypeDetail,
    StyleList,
    StyleDetail,
)

app_name = "courses_api"
user_urls = [
    path("<int:pk>/", UserDetail.as_view(), name="user-detail"),
]

payment_urls = [
    path(
        "course/<int:pk>/", CoursePaymentDetail.as_view(), name="course-payment-detail"
    ),
    path(
        "subscription/<int:pk>/",
        SubscriptionPayment.as_view(),
        name="subscription-payment",
    ),
]

offering_urls = [
    path("<int:pk>/", OfferingDetail.as_view(), name="offering-detail"),
]

newsletter_urls = []

urlpatterns = [
    path("", OfferingList.as_view(), name="offering-list"),
    path("users/", include(user_urls)),
    path("payment/", include(payment_urls)),
    path("offering/", include(offering_urls)),
    path("newsletter/", include(newsletter_urls)),
    path("email_addresses/", FilteredEmailList.as_view(), name="email_address-list"),
    path("coursetype/<int:pk>/", CourseTypeDetail.as_view(), name="coursetype-detail"),
    path("style/", StyleList.as_view(), name="style-list"),
    path("style/<int:pk>/", StyleDetail.as_view(), name="style-detail"),
]
