import csv
from django.core.management.base import BaseCommand
from shop.models import CDOffer

class Command(BaseCommand):
    help = 'Eksportuje listę aktualnie dostępnych płyt na giełdzie do pliku CSV'

    def handle(self, *args, **kwargs):
        # Pobieramy tylko te płyty, które nie zostały jeszcze kupione
        active_offers = CDOffer.objects.filter(orders__isnull=True).order_by('-created_at')
        
        # Nazwa pliku wyjściowego
        filename = 'katalog_plyt.csv'
        
        # Otwieramy plik do zapisu
        # Używamy encoding='utf-8-sig', aby polskie znaki poprawnie wyświetlały się w Excelu
        with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
            # Używamy średnika jako separatora (standard dla polskiego Excela)
            writer = csv.writer(file, delimiter=';')
            
            # Zapisujemy pierwszy wiersz - nagłówki kolumn
            writer.writerow(['Tytuł', 'Wykonawca', 'Cena (PLN)', 'Stan', 'Sprzedawca', 'Data wystawienia'])
            
            # Pętla zapisująca każdą płytę jako osobny wiersz
            for offer in active_offers:
                # get_condition_display() zamienia 'NEW'/'USED' na 'Nowa'/'Używana'
                writer.writerow([
                    offer.title,
                    offer.artist.name,
                    offer.price,
                    offer.get_condition_display(),
                    offer.seller.username,
                    offer.created_at.strftime('%Y-%m-%d %H:%M')
                ])
                
        self.stdout.write(self.style.SUCCESS(f'Sukces! Wyeksportowano {active_offers.count()} aktualnych ofert do pliku {filename}.'))