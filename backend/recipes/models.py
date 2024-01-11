from colorfield import fields
from django.db import models
from django.db.models import UniqueConstraint
from api.validators import not_null
from users.models import CustomUser


class Ingredient(models.Model):
    """
    Модель ингредиентов и их количества
    """

    name = models.CharField(
        verbose_name="Наименование",
        unique=True,
        max_length=200,
        blank=False)
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=200,
        blank=False
    )

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиентов"
        ordering = ["id"]
        constraints = [
            UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="ingredient_name_measurement_unit"
            )
        ]

    def __str__(self):
        return f"{self.name[:15]} - {self.measurement_unit}"


class Tag(models.Model):
    """
    Модель тегов
    """

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
    slug = models.SlugField(
        verbose_name="Слаг",
        max_length=200,
        unique=True
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name[:15]


class Recipe(models.Model):
    """
    Модель рецептов
    """
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientCount",
        verbose_name="Игредиент"
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор"
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги"
    )
    image = models.ImageField(
        upload_to="recipes/",
        blank=False,
        verbose_name="Картинка")
    name = models.CharField(
        verbose_name="Наименование рецепта",
        max_length=200,
        blank=False
    )
    text = models.TextField(
        verbose_name="Описание рецепта",
        blank=False
    )
    cooking_time = models.IntegerField(
        verbose_name="Время приготовления",
        validators=[not_null],
        blank=False
    )
    pub_date = models.DateTimeField("Дата публикации",
                                    auto_now_add=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name[:15]


class RecipeTag(models.Model):
    """
    RecipeTag - это класс модели, который представляет связь между рецептами и
    тегами в приложении.Он содержит два ForeignKey, которые связывают его с
    моделями Recipe и Tag.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("recipe", "tag")


class IngredientCount(models.Model):
    """
    Модель для связи ингредиентов и рецептов
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="ingredient_count"
    )

    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        related_name="ingredient_count"
    )

    amount = models.PositiveIntegerField(
        validators=[not_null],
        verbose_name="Подсчёт ингредиентов"
    )

    class Meta:
        default_related_name = "Ingredient_Count"
        constraints = [
            models.UniqueConstraint(fields=("recipe", "ingredients"),
                                    name="Ingredient_Count")]

    def __str__(self) -> str:
        return f"{self.amount} {self.ingredients}"


class FavRecipes(models.Model):
    """
    Модель для добавления рецептов в избранное
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",)

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        default_related_name = "fav_recipes"
        constraints = [
            models.UniqueConstraint(fields=("user", "recipe"),
                                    name="fav_recipes_list")]

    def __str__(self):
        return (f"рецепт- {self.recipe.name[:15]}"
                f"добавлен в избранное к  {self.user.username[:15]}"
                )


class ShoppingList(models.Model):
    """
    Модель для списка покупок
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",)

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
        default_related_name = "shopping_list"
        constraints = [
            models.UniqueConstraint(fields=("user", "recipe"),
                                    name="user_shopping_list")]

    def __str__(self):
        return (f"рецепт- {self.recipe.name[:15]}"
                f"добавлен в список покупок к   {self.user.username[:15]}")
