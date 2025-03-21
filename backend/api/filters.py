from django.db.models import Exists, OuterRef
from django_filters import rest_framework as filters
from django.db.models import Q

from recipes.models import Recipe, ShoppingCart, Favorite


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')
    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
        
    def filter_tags(self, queryset, name, value):
        tag_slugs = self.request.GET.getlist('tags')  # Получаем список значений tags

        if not tag_slugs:
            return queryset

        # Фильтрация через Q (ИЛИ)
        query = Q()
        for slug in tag_slugs:
            query |= Q(tags__slug=slug)

        return queryset.filter(query).distinct()

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.annotate(
                in_favorite=Exists(Favorite.objects.filter(
                    user=user, recipe=OuterRef('pk'))
                )
            ).filter(in_favorite=True)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.annotate(
                in_cart=Exists(ShoppingCart.objects.filter(
                    user=user, recipe=OuterRef('pk'))
                )
            ).filter(in_cart=True)
        return queryset
