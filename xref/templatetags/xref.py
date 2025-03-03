from django import template
from django.utils.html import mark_safe
from django.template.defaultfilters import escapejs


register = template.Library()

@register.filter()
def xref_status_badge(o):
    if o.xref_status == 'draft':
        color = 'bg-danger'
    elif o.xref_status == 'ready':
        color = 'bg-warning'
    elif o.xref_status == 'verified':
        color = 'bg-success'
    return mark_safe(f'<span class="badge {color}">{ o.xref_status }</span>')

@register.filter()
def as_params(selections):
    return mark_safe('&'.join([ k + '=' + v for k, v in selections.items() ]))

@register.filter()
def get_preceding_requirement(sections, n):
    for section in reversed(sections[0:n-1]):
        requirement = section.requirements.order_by('-index').first()
        if requirement:
            return requirement
    return None

@register.filter()
def get_following_requirement(sections, n):
    for section in sections[n+1:]:
        requirement = section.requirements.order_by('index').first()
        if requirement:
            return requirement
    return None

@register.filter()
def js_str(u):
    return mark_safe(str(u))

@register.filter()
def next_item(value, n):
    try:
        return value[int(n)+1]
    except:
        return None

@register.filter()
def prev_item(value, n):
    try:
        return value[int(n)-1]
    except:
        return None

@register.simple_tag
def requirement_is_selected(current_requirement, selected_requirement, selected_statement):
    return current_requirement == selected_requirement and selected_statement is None
    
@register.simple_tag
def statement_is_selected(current_statement, selected_statement, selected_constraint):
    return current_statement == selected_statement and selected_constraint is None
    
@register.simple_tag
def constraint_is_selected(current_constraint, selected_constraint):
    return current_constraint == selected_constraint
    
@register.simple_tag
def cond_assignment(cond, true_value, false_value):
    if cond:
        return true_value
    return false_value
