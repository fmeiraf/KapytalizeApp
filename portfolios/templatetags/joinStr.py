from django import template
import datetime

register = template.Library()

@register.filter
def joinStr(value1, value2):
    return str(value1) + str(value2).replace(" ",'')
