import re

from django.core.validators import RegexValidator

REGEX_USERNAME = re.compile(r'^[\w.@+-]+')

# Валидация логина
USERNAME_VALIDATOR = RegexValidator(
    regex=REGEX_USERNAME,
    message='Для имени доступны буквы A - Z,  a - z и символы _.+-@'
)
