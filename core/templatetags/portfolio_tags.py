from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter: {{ "a,b,c"|split:"," }}"""
    return [item.strip() for item in value.split(delimiter) if item.strip()]

@register.filter
def add_str(value, arg):
    return str(value) + str(arg)
