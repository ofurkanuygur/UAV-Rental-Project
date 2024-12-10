from django import template

register = template.Library()

@register.filter
def percentage(value, total):
    try:
        if total > 0:
            return (value / total) * 100
        return 0
    except (ValueError, ZeroDivisionError):
        return 0