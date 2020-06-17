from django import template

register = template.Library()

@register.filter(name='replace_semi_colon')
def replace(value, arg):
    return value.replace(arg, ', ')

@register.filter(name='utcfmt')
def utcfmt(arg):
    if arg is not None:
        return arg.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        return