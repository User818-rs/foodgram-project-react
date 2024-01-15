import re

from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_symbols_in_fields(value):
    """
    Валидатор для проверки наличия недопустимых символов в строке.
    """
    regex = re.findall(r"[^\w.@+-]+", value)
    if regex:
        raise ValidationError(
            f"Недопустимый символ в строке: {', '.join(regex)}"
        )
    return value


def validate_me(value):
    """
    Валидатор для проверки использования запрещенного значения "me".
    """
    if value == "me":
        raise serializers.ValidationError("Использовать имя ME запрещено!")
    return value


def not_null(value):
    """
    Валидатор для проверки, что значение не равно нулю.
    """
    if value < 1:
        raise ValidationError("Значение не может быть меньше 1 грамма")
    return value
