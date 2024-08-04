from django import template
from django.utils.html import mark_safe

register = template.Library()

from ..models import Answer

@register.filter
def answer(obj, question):
    val = getattr(obj, question.name)
    a = Answer.objects.get(question=question.name, low__lte=val, high__gte=val)
    return mark_safe(a.text_en)
