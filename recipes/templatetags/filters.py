from django import template

register = template.Library()
# Filter replace semi-colons to comma in lists stored in a database
@register.filter(name='replace_semi_colon')
def replace(value, arg):
    return value.replace(arg, ', ')
# Filter to convert date to isostring
@register.filter(name='utcfmt')
def utcfmt(arg):
    if arg is not None:
        return arg.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        return