from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class ShoppingFavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]

    def create(self, request, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        obj, created = self.queryset.get_or_create(
            user=request.user, recipe=recipe)
        serializer = self.get_serializer(obj)
        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        get_object_or_404(Recipe, pk=recipe_id)
        obj = self.queryset.filter(
            user=request.user, recipe=recipe_id)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
