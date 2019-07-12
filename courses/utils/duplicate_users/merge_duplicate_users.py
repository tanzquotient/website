import logging

from django.contrib.auth.models import User

from courses.models import UserProfile

log = logging.getLogger('merge_duplicate_users')


def merge_duplicate_users(to_merge):
    for primary, aliases in to_merge.items():
        user = User.objects.get(id=primary)
        user_aliases = list(User.objects.filter(id__in=aliases))
        user.date_joined = User.objects.filter(id__in=aliases).order_by("date_joined").first().date_joined

        log.info("Merging {}".format(user))

        profile = user.profile
        profile.legi = _get_value_from_most_recent_alias_profile(aliases, profile, "legi")
        profile.address = _get_value_from_most_recent_alias_profile(aliases, profile, "address")
        profile.phone_number = _get_value_from_most_recent_alias_profile(aliases, profile, "phone_number")
        profile.student_status = _get_value_from_most_recent_alias_profile(aliases, profile, "student_status")
        profile.body_height = _get_value_from_most_recent_alias_profile(aliases, profile, "body_height")
        profile.about_me = _get_value_from_most_recent_alias_profile(aliases, profile, "about_me")
        profile.birthdate = _get_value_from_most_recent_alias_profile(aliases, profile, "birthdate")
        profile.nationality = _get_value_from_most_recent_alias_profile(aliases, profile, "nationality")
        profile.residence_permit = _get_value_from_most_recent_alias_profile(aliases, profile, "residence_permit")
        profile.ahv_number = _get_value_from_most_recent_alias_profile(aliases, profile, "ahv_number")
        profile.bank_account = _get_value_from_most_recent_alias_profile(aliases, profile, "bank_account")
        profile.default_hourly_wage = _get_value_from_most_recent_alias_profile(aliases, profile, "default_hourly_wage")

        profile.save()
        user.save()

        for alias in user_aliases:
            try:
                profile = alias.profile
                profile.delete()
            except UserProfile.DoesNotExist:
                pass

            for subscription in alias.subscriptions.all():
                subscription.user = user
                subscription.save()

            for subscription in alias.subscriptions_as_partner.all():
                subscription.partner = user
                subscription.save()

            for survey_instance in alias.survey_instances.all():
                survey_instance.user = user
                survey_instance.save()

            for organising in alias.organising.all():
                organising.organiser = user
                organising.save()

            for teaching in alias.teaching_courses.all():
                teaching.teacher = user
                teaching.save()

            for teaching in alias.teaching_lessons.all():
                teaching.teacher = user
                teaching.save()

            for function in alias.functions.all():
                function.users.remove(alias)
                function.users.add(user)
                function.save()

            alias.delete()


def _get_value_from_most_recent_alias_profile(alias_ids, profile, field):

    value = getattr(profile, field)
    if value:
        return value

    for user in User.objects.filter(id__in=alias_ids).order_by("-last_login"):
        try:
            profile = user.profile
            value = getattr(profile, field)
            if value:
                return value
        except UserProfile.DoesNotExist:
            pass

    return None
