import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_alphanumeric(value):
    """Проверяет, что полученные символы принадлежат анг. алфавиту и числам."""
    pattern = re.compile(r'^[a-zA-Z0-9]+$')
    if not pattern.match(value):
        raise ValidationError(
            'The value should contain only alphanumeric characters'
        )


def score_validator(value):
    """Проверяет, что полученное значение находится в пределах от 0 до 10."""
    if value < 0 or value > 10:
        raise ValidationError('Score must be between 0 and 10')


def validate_year(value):
    """Проверяет, что год не превышает текущий."""
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError('Year cannot be in the future')
