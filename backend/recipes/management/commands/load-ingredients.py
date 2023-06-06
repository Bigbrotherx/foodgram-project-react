import json

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient

MODEL_AND_FILE_TABLE = {
    Ingredient: "ingredients.json",
}


def check_exists_models(table):
    for model, _ in table.items():
        if model.objects.exists():
            print("Такие данные уже существуют")
            continue


class Command(BaseCommand):
    """
    Команда для переноса данных из csv-файлов в БД Django.

    При старте осуществляет дополнительно простую проверку,
    существуют ли такие модели данных в БД.
    """

    help = "Import csv to models in Django db"

    def handle(self, *args, **kwargs):
        check_exists_models(MODEL_AND_FILE_TABLE)

        for model, file in MODEL_AND_FILE_TABLE.items():
            file_location = f"{settings.BASE_DIR}/static/data/{file}"

            with open(file_location, "r", encoding="utf-8") as json_file:
                reader = json.load(json_file)
                for row in reader:
                    if model == Ingredient:
                        data = model(
                            name=row["name"],
                            measurement_unit=row["measurement_unit"],
                        )
                        data.save()
