from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import CDOffer, Order

class Command(BaseCommand):
    help = 'Wyświetla krótkie podsumowanie statystyk sklepu'

    def handle(self, *args, **kwargs):
        users_count = User.objects.count()
        
        # Liczy wszystkie płyty (sprzedane i niesprzedane)
        total_offers_count = CDOffer.objects.count()
        
        # Liczy tylko te płyty, które nie mają jeszcze żadnego przypisanego zamówienia
        active_offers_count = CDOffer.objects.filter(orders__isnull=True).count()
        
        orders_count = Order.objects.count()

        self.stdout.write(self.style.WARNING('--- STATYSTYKI GIEŁDY PŁYT ---'))
        self.stdout.write(f'Zarejestrowani użytkownicy: {users_count}')
        self.stdout.write(f'Wszystkie płyty w historii: {total_offers_count}')
        self.stdout.write(f'Płyty aktualnie dostępne do kupienia: {active_offers_count}')
        self.stdout.write(f'Złożone zamówienia: {orders_count}')
        self.stdout.write(self.style.WARNING('------------------------------'))