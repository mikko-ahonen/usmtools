from django.urls.converters import StringConverter

class LangConverter(StringConverter):
    regex = r'\w\w'

class UsernameConverter(StringConverter):
    regex = r'\w{3,}'
