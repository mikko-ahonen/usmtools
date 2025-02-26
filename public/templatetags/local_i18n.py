from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()

@register.filter()
def language_name(language_code):
    LANGUAGE_NAMES = {
        "fi": _('Finnish'),
        "en": _('English'),
        "nl": _('Dutch'),
    }
    return LANGUAGE_NAMES[language_code]
