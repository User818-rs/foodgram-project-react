import re
from rest_framework import serializers
from django.core.exceptions import ValidationError


def validate_symbols_in_fields(value):
    regex = re.findall(r'[^\w.@+-]+', value)
    if regex:
        raise ValidationError(
            f"Недопустимый символ в строке: {', '.join(regex)}"
        )
    return value


def validate_me(value):
    if value == 'me':
        raise serializers.ValidationError('Использовать имя ME запрещено!')
    return value

def not_null(value):
    if value < 1:
        raise ValidationError(
            f"Значение не может быть меньше 1 грамма"
        )
    return value