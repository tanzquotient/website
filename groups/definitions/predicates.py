def is_teacher(user):
    return user.profile.is_teacher()

def is_current_teacher(user):
    return user.profile.is_current_teacher()

def newsletter(user):
    return user.profile.newsletter

def get_involved(user):
    return user.profile.get_involved

def is_board_member(user):
    return user.functions.exists()
