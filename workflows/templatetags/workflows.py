from django import template

register = template.Library()

@register.filter
def instruction_for(action, profile):
    return action.tasks
