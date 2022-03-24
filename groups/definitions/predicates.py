from django.contrib.auth.models import User


def is_teacher(user: User) -> bool:
    return user.profile.is_teacher()


def is_current_teacher(user: User) -> bool:
    return user.profile.is_current_teacher()


def newsletter(user: User) -> bool:
    return user.profile.newsletter


def get_involved(user: User) -> bool:
    return user.profile.get_involved


def is_board_member(user: User) -> bool:
    return user.functions.exists()
