from django.conf.urls import url, include

from .api import *

# # Routers provide an easy way of automatically determining the URL conf.
# router = routers.DefaultRouter()
# router.register(r'users', UserList)
# router.register(r'user', UserDetail)
# router.register(r'course', CourseDetail)

app_name = 'courses_api'
user_urls = [
    url(r'^(?P<pk>\d+)/$', UserDetail.as_view(), name='user-detail'),
]

payment_urls = [
    url(r'^course/(?P<pk>\d+)/$', CoursePaymentDetail.as_view(), name='course-payment-detail'),
    url(r'^subscription/(?P<pk>\d+)/$', SubscriptionPayment.as_view(),
        name='subscription-payment'),
]

offering_urls = [
    url(r'^(?P<pk>\d+)/$', OfferingDetail.as_view(), name='offering-detail'),
]

newsletter_urls = [
]

urlpatterns = [url(r'^$', OfferingList.as_view(), name='offering-list'),
               url(r'^users/', include(user_urls)),
               url(r'^payment/', include(payment_urls)),
               url(r'^offering/', include(offering_urls)),
               url(r'^newsletter/', include(newsletter_urls)),
               url(r'^email_addresses/$', FilteredEmailList.as_view(), name='email_address-list'),
               url(r'^coursetype/(?P<pk>\d+)/$', CourseTypeDetail.as_view(), name='coursetype-detail'),
               url(r'^style/$', StyleList.as_view(), name='style-list'),
               url(r'^style/(?P<pk>\d+)/$', StyleDetail.as_view(), name='style-detail'),
               ]
