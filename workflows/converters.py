from django.urls.converters import StringConverter
from .rasci import RASCI

class ResponsibilityTypesConverter(StringConverter):
    regex = RASCI.REGEX
