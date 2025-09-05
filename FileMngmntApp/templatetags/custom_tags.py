from django import template
from datetime import date, datetime


register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')

@register.filter
def format_date_auto(value):
    if isinstance(value, (date, datetime)):
        return value.strftime('%d-%m-%Y ')
    return value