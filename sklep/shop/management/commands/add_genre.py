from django.core.management.base import BaseCommand
from shop.models import Genre

class Command(BaseCommand):
    help = 'Dodaje nowy gatunek muzyczny do bazy danych'

    def add_arguments(self, parser):
        # Definiujemy, że komenda oczekuje jednego argumentu (nazwy gatunku)
        parser.add_argument('genre_name', type=str, help='Nazwa gatunku do dodania')

    def handle(self, *args, **kwargs):
        # Pobieramy nazwę wpisaną w terminalu
        genre_name = kwargs['genre_name']
        
        # get_or_create sprawdzi, czy gatunek już istnieje. Jeśli nie, to go stworzy.
        genre, created = Genre.objects.get_or_create(name=genre_name)
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Sukces: Dodano nowy gatunek "{genre_name}".'))
        else:
            self.stdout.write(self.style.WARNING(f'Uwaga: Gatunek "{genre_name}" już istnieje w bazie.'))