import csv

from django.core.management import BaseCommand

from reviews.models import (Title, Genre, Category, User,
                            Review, Comment)

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the child data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""
FILES = [
    'users.csv', 'category.csv', 'genre.csv', 'titles.csv', 'review.csv',
    'comments.csv', 'genre_title.csv',
]
MODELS = [User, Category, Genre, Title, Review, Comment, Title.genre.through]


def import_csv(file, model):
    with open(file, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        print(file)
        for row in reader:
            model.objects.create(**row)


class Command(BaseCommand):
    help = "Loads data from somefiles.csv"

    def handle(self, *args, **options):
        for model in MODELS:
            if model.objects.exists():
                print(model, ' data already loaded....')
                print("Deleting data")
                model.objects.all().delete()
                print("Data is deleted")
        print("Loading data")
        for file, model in zip(FILES, MODELS):
            import_csv(f'static/data/{file}', model)
