import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

class RestrictedUsernameValidator(validators.RegexValidator):
    regex = r'^[A-Za-z0-9_]{3,}\Z'
    message = _(
        'Enter a valid username. This value may contain only English letters, '
        'numbers, and underscore characters. It must be at three characters at the minimum.'
    )
    flags = re.ASCII
