from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter()
def step_process_badge(step):
    process = step.process
    process_name = step.get_process_display()
    return mark_safe(f'<span class="align-middle badge small-badge rounded-pill {process}-bg">{ process_name }</span>')
