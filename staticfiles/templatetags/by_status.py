from django import template

register = template.Library()

@register.filter
def by_status(entity, status):
    return entity.filter(status=status)
