from django import template

register = template.Library()

@register.filter(name='split')
def split(value, key):
    """
    Returns the value turned into a list.
    """
    return value.split(key)

@register.filter(name='replace')
def replace(value, arg):
    """Custom template filter to replace characters in strings."""
    original, new = arg.split(',')
    return value.replace(original, new)

@register.filter(name='multiply')
def multiply(value, multiplier):
    try:
        return value * int(multiplier)
    except (ValueError, TypeError):
        return 0