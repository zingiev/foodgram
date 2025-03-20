from django.contrib import admin
from django.db.models import Count

from .models import Recipe, Tag, Ingredients, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    readonly_fields = ('favorite_count',)
    search_fields = ('author', 'name')
    list_filter = ('tags',)
    filter_horizontal = ('ingredients',)
    inlines = [RecipeIngredientInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(favorite_count=Count('recipefavorites'))

    def favorite_count(self, obj):
        return obj.favorite_count
    favorite_count.short_description = "Добавлений в избранное"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
