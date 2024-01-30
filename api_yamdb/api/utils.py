import re

from rest_framework import serializers

from users.constants import USERNAME_PATTERN


def validate_username(username):
    if not re.match(USERNAME_PATTERN, username):
        raise serializers.ValidationError(
            'Username should contain '
            'only letters, digits, and @/./+/-/_ characters.'
        )
    return username


def validate_email(email):
    if len(email) > 254:
        raise serializers.ValidationError('Too long email')
    return email
