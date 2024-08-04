from django import template

register = template.Library()

@register.filter(name='get_max_depth') 
def get_max_depth(steps):
    return max(x.process_depth for x in steps)
