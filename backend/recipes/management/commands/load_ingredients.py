import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredients


class Command(BaseCommand):
    help = "Загружает ингредиенты из JSON-файла"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Путь к JSON-файлу")

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if not isinstance(data, list):
                self.stderr.write(self.style.ERROR(
                    "Ошибка: JSON должен содержать список объектов"))
                return

            ingredients = []
            for item in data:
                ingredients.append(Ingredients(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']))

            Ingredients.objects.bulk_create(
                ingredients, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(
                f"Успешно загружено {len(ingredients)} ингредиентов"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка при загрузке: {e}"))
