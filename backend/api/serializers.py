from rest_framework import serializers

from recipes.models import Tag
from .validators import slug_by_pattern


class TagSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')

    def validate_slug(self, value):
        slug_by_pattern(value)
        return value
