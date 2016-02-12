from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

def fence_helper(value, s):
    return s+value+s

@register.filter(needs_autoescape=False)
def fence(value, s):
    if isinstance(value, basestring):
        return fence_helper(value, s)
    elif isinstance(value, list):
        return map(lambda v: fence_helper(v, s), value)
    else:
        return fence_helper(unicode(value), s)
