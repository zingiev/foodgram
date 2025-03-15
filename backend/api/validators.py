import re

from rest_framework import serializers

from core.constants import (
    PATTERN_VALID_USERNAME,
    URL_PATH_ME,
    PATTERN_TAG_SLUG
)


def username_by_pattern(username):
    is_valid_username = re.match(PATTERN_VALID_USERNAME, username)
    if not is_valid_username:
        raise serializers.ValidationError()
    return username


def username_by_path_me(username):
    if username == URL_PATH_ME:
        raise serializers.ValidationError(
            {"username": f'Под именем "{URL_PATH_ME}" '
                         f'нельзя регистрироваться'}
        )
    return username


def slug_by_pattern(slug):
    is_valid_slug = re.match(PATTERN_TAG_SLUG, slug)
    if not is_valid_slug:
        raise serializers.ValidationError()
    return slug
