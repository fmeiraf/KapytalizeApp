from django import template
import datetime

register = template.Library()

@register.filter
def removeBlank(value1):
    return str(value1).replace(" ",'')
