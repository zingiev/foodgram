from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from .serializers import CustomUserSerialier


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerialier
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post']
    permission_classes = [AllowAny]

    def get_queryset(self):
        return self.queryset
