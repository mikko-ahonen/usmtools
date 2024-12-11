from django import template

register = template.Library()

@register.filter
def by_status(entity, statuses):
    return entity.filter(status__in=statuses)
