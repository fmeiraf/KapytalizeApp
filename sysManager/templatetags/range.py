from django import template
import datetime

register = template.Library()

@register.filter
def temp_range(value):
    return range(1,value)
