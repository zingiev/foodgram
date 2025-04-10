import base64
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                img_bytes = base64.b64decode(imgstr)
                image = Image.open(BytesIO(img_bytes))
                image.verify()
                file = ContentFile(img_bytes, name='temp.' + ext)
                return super().to_internal_value(file)
            except Exception:
                raise serializers.ValidationError(
                    'Невалидный формат изображения.')
        return super().to_internal_value(data)
