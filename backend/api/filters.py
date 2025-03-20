import django_filters
from django.db.models import Exists, OuterRef
from recipes.models import Recipe, Favorite, ShoppingCart


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = []

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(Exists(Favorite.objects.filter(
                user=user, recipe=OuterRef('pk'))))
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(Exists(ShoppingCart.objects.filter(
                user=user, recipe=OuterRef('pk'))))
        return queryset
