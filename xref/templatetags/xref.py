from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter()
def xref_status_badge(o):
    if o.xref_status == 'draft':
        color = 'bg-danger'
    elif o.xref_status == 'ready':
        color = 'bg-success'
    elif o.xref_status == 'approved':
        color = 'bg-primary'
    return mark_safe(f'<span class="badge {color}">{ o.status }</span>')

@register.filter()
def as_params(selections):
    return mark_safe('&'.join([ k + '=' + v for k, v in selections.items() ]))
