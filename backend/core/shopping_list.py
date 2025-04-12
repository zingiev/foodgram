from collections import defaultdict

from recipes.models import RecipeIngredient


def generate_shopping_list(shopping_cart_queryset):
    ingredients_dict = defaultdict(lambda: {'amount': 0, 'unit': ''})

    for cart_item in shopping_cart_queryset:
        recipe = cart_item.recipe
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe=recipe
        ).select_related('ingredient')

        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient.ingredient
            key = ingredient.name
            ingredients_dict[key]['amount'] += recipe_ingredient.amount
            ingredients_dict[key]['unit'] = ingredient.measurement_unit

    return "\n".join(
        f"{name} ({data['unit']}) — {data['amount']}"
        for name, data in ingredients_dict.items()
    )
