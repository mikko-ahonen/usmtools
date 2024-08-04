from django import template

register = template.Library()

@register.filter
def raci(responsible):
    if responsible:
        return responsible.get_types_display()
    else:
        return '' 
