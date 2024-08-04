from django import template

register = template.Library()

@register.filter(name='times') 
def times(number, extra=0):
    return range(number + extra)
