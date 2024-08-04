from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter
def score(obj, question):
    val = getattr(obj, question.name)
    return mark_safe(str(int(val / 7 * 100)))
