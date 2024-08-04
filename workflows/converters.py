from django.urls.converters import StringConverter
from .raci import RACI

class ResponsibilityTypesConverter(StringConverter):
    regex = RACI.REGEX
