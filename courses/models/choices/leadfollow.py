from django.utils.translation import gettext_lazy as _


class LeadFollow:
    LEAD = 'l'
    FOLLOW = 'f'
    NO_PREFERENCE = 'n'

    CHOICES = (
        (LEAD, _('lead')),
        (FOLLOW, _('follow')),
        (NO_PREFERENCE, _('no preference'))
    )

    @staticmethod
    def partner(preference):
        if preference == LeadFollow.LEAD:
            return LeadFollow.FOLLOW
        if preference == LeadFollow.FOLLOW:
            return LeadFollow.LEAD
        return LeadFollow.NO_PREFERENCE

    @staticmethod
    def is_compatible(preference_a, preference_b):
        return (preference_a, preference_b) in [
            (LeadFollow.LEAD, LeadFollow.FOLLOW),
            (LeadFollow.LEAD, LeadFollow.NO_PREFERENCE),

            (LeadFollow.FOLLOW, LeadFollow.LEAD),
            (LeadFollow.FOLLOW, LeadFollow.NO_PREFERENCE),

            (LeadFollow.NO_PREFERENCE, LeadFollow.LEAD),
            (LeadFollow.NO_PREFERENCE, LeadFollow.FOLLOW),
            (LeadFollow.NO_PREFERENCE, LeadFollow.NO_PREFERENCE),
        ]
