from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from colorfield import fields

from foodgram.constants import (
    MAX_AMOUNT,
    MAX_COOKING_TIME,
    MIN_AMOUNT,
    MIN_COOKING_TIME,
)
from users.models import CustomUser


class Ingredient(models.Model):
    """Модель ингредиентов и их количества."""

    name = models.CharField(
        verbose_name="Наименование", unique=True, max_length=200, blank=False
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения", max_length=200, blank=False
    )

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"
        ordering = ["id"]
        constraints = [
            UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="ingredient_name_measurement_unit",
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.measurement_unit}"


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name="Наименование",
        unique=True,
        max_length=200,
    )
    color = fields.ColorField(
        verbose_name="Цвет в HEX",
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(verbose_name="Слаг", max_length=200, unique=True)

    class Meta:
        ordering = ("id",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientCount",
        verbose_name="Игредиент",
        related_name="recipes_ingredient",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги")
    image = models.ImageField(
        upload_to="recipes/", blank=False, verbose_name="Картинка"
    )
    name = models.CharField(
        verbose_name="Наименование рецепта", max_length=200, blank=False
    )
    text = models.TextField(verbose_name="Описание рецепта", blank=False)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(
                limit_value=MIN_COOKING_TIME,
            ),
            MaxValueValidator(
                limit_value=MAX_COOKING_TIME,
            ),
        ],
        blank=False,
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """
    RecipeTag - это класс модели, который представляет связь между рецептами и
    тегами в приложении.Он содержит два ForeignKey, которые связывают его с
    моделями Recipe и Tag.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_tag_recipe",
        verbose_name="Рецепт"
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="recipe_tag_tag",
        verbose_name="Тэг"
    )

    class Meta:
        unique_together = ("recipe", "tag")

    def __str__(self) -> str:
        return f"{self.recipe} {self.tag}"


class IngredientCount(models.Model):
    """Модель для связи ингредиентов и рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="ingredient_count_recipe",
    )

    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        related_name="ingredient_count_ingredients",
    )

    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=MIN_AMOUNT,
            ),
            MaxValueValidator(
                limit_value=MAX_AMOUNT,
            ),
        ],
        verbose_name="Подсчёт ингредиентов",
    )

    class Meta:
        default_related_name = "ingredient_count"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredients"), name="ingredient_count"
            )
        ]

    def __str__(self) -> str:
        return f"{self.amount} {self.ingredients}"


class FavoriteRecipe(models.Model):
    """Модель для добавления рецептов в избранное."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favorite",
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="favorite",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="favorite_recipe_list"
            )
        ]

    def __str__(self):
        return (
            f"рецепт- {self.recipe.name}"
            f"добавлен в избранное к  {self.user.username}"
        )


class ShoppingList(models.Model):
    """Модель для списка покупок."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="shopping_list_user",
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="shopping_list_recipe",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
        default_related_name = "shopping_list"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="user_shopping_list"
            )
        ]

    def __str__(self):
        return (
            f"рецепт- {self.recipe.name}"
            f"добавлен в список покупок к   {self.user.username}"
        )
