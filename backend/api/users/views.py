from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, GetTokenSerializer
from core.constants import URL_PATH_ME


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post']
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination
    
    @action(methods=['get'],
            detail=False,
            url_path=URL_PATH_ME,
            permission_classes=(IsAuthenticated,)
    )
    def get_user_me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class APIGetTokenVeiw(APIView):

    @staticmethod
    def generate_jwt_token(user):
        auth_token = RefreshToken.for_user(user).access_token
        return {'auth_token': str(auth_token)}

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user = get_object_or_404(User, email=email)
        auth_token = self.generate_jwt_token(user)
        return Response(auth_token, status=status.HTTP_200_OK)
