from email_system.models import UnsubscribeCode
from groups.definitions import GroupDefinitions

def unsubscribe(context, user_id, code):
    unsubscribe_code = UnsubscribeCode.objects.filter(user_id=user_id)
    if not unsubscribe_code.exists():
        return False

    if context == GroupDefinitions.NEWSLETTER.name:
        profile = unsubscribe_code.user.profile
        profile.newsletter = False
        profile.save()
        return True

    if context == GroupDefinitions.GET_INVOLVED.name:
        profile = unsubscribe_code.user.profile
        profile.get_involved = False
        profile.save()
        return True

    return False