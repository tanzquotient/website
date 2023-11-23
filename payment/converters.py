from django.urls.converters import StringConverter


class UsiPathConverter(StringConverter):
    regex = "[a-zA-Z0-9]{6}"
