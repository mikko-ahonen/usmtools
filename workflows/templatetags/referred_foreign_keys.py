from django import template
from django.utils.html import mark_safe
from django.db.models.fields.related import ForeignObjectRel

register = template.Library()

@register.filter()
def referred_foreign_keys(obj):
    #links = [field.get_accessor_name() for field in obj._meta.get_fields() if issubclass(type(field), ForeignObjectRel)]
    links = [(field.get_accessor_name(), getattr(obj, field.get_accessor_name()), field) for field in obj._meta.get_fields() if issubclass(type(field), ForeignObjectRel)]
    return links
