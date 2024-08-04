from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter()
def status_badge(o):
    if o.status == 'draft':
        color = 'bg-danger'
    elif o.status == 'ready':
        color = 'bg-success'
    elif o.status == 'approved':
        color = 'bg-primary'
    return mark_safe(f'<span class="badge {color}">{ o.status }</span>')
