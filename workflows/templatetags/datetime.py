from django import template
from django.conf import settings
from django.utils.html import mark_safe
import datetime

register = template.Library()

@register.filter(name='datetime')
def datetime_(ts, default='', fmt=settings.DATETIME_FORMAT):
    if isinstance(ts, datetime.datetime):
        return mark_safe(ts.strftime(fmt))
    else:
        return default
