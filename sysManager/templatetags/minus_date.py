from django import template
import datetime

register = template.Library()

@register.filter
def minus_date_in_days(lastdate, updatedate):
    dif = lastdate - updatedate
    return dif.days
