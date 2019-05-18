from django import forms

from courses.forms import SingleSubscriptionForm
from courses.models import UserProfile
        

class CoupleSubscriptionForm(SingleSubscriptionForm):

    # helper function that checks if the email address belongs to a user
    def validate_user_email(self):
        # an empty address is ok
        if not self:
            return
        users = UserProfile.objects.filter(user__email=self)
        # the email does not belong to a valid user account
        if len(users) == 0:
            raise forms.ValidationError('There is no user for the email address you entered for your partner!')

    partner_email = forms.EmailField(required=False, validators=[validate_user_email])
