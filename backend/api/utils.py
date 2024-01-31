from io import BytesIO

from django.db.models import Sum

from recipes.models import IngredientCount


def create_shopping_list_file(shopping_cart, user=None):
    """
    Создает файл с списком покупок из корзины покупок.
        Параметры:
    shopping_cart (IngredientCount): Объект корзины покупок.
    user (User, необязательно): Объект пользователя. По умолчанию None.

        Возвращает:
    BytesIO: Объект BytesIO, содержащий файл списка покупок.
    """
    shopping_cart = IngredientCount.objects.filter(
        recipe__shopping_list_recipe__user=user).values(
            'ingredients__name', 'ingredients__measurement_unit').annotate(
                amount=Sum('amount')).order_by('ingredients__name')
    shopping_list = []
    for ingredient in shopping_cart:
        shopping_list.append(
            f"{ingredient['ingredients__name']} "
            f"({ingredient['ingredients__measurement_unit']}) -"
            f"{ingredient['amount']}\n")
    content_str = ''.join(shopping_list)
    buffer = BytesIO()
    buffer.write(content_str.encode('utf-8'))
    return buffer
