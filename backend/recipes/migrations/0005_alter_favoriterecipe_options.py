# Generated by Django 4.2.7 on 2024-02-07 06:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_ingredientcount_ingredients_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favoriterecipe',
            options={'default_related_name': 'favorite', 'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
    ]
