from constants import CSV_PATH
import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загрузка данных из CSV-файла в БД"

    def handle(self, *args, **kwargs):
        with open(CSV_PATH, encoding='utf-8') as file:
            csvreader = csv.reader(file)
            next(csvreader)
            for row in csvreader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1],
                )
