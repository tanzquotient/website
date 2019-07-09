from courses.models import CourseSubscriptionType


def _course_filter_style(c, style_name, filter_styles):
    if style_name is None:
        return True

    if style_name.lower() == "all":
        return True

    if style_name.lower() == "other":
        for s in filter_styles:
            if c.has_style(s.name):
                return False
        return True

    return c.has_style(style_name)


def _course_filter_type(c, subscription_type):
    if subscription_type.lower() == "regular" and c.subscription_type != CourseSubscriptionType.REGULAR:
        return False

    if subscription_type.lower() == "open_class" and c.subscription_type != CourseSubscriptionType.OPEN_CLASS:
        return False

    if subscription_type.lower() == "external" and c.subscription_type != CourseSubscriptionType.EXTERNAL:
        return False

    return True


def course_filter(c, preview_mode, subscription_type, style_name, filter_styles):
    if not c.is_displayed(preview_mode):
        return False

    if c.is_over():
        return False

    return _course_filter_style(c, style_name, filter_styles) and _course_filter_type(c, subscription_type)
