from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import CDOffer
from .models import Order
from .models import Artist, Genre

class ShopBasicTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.artist = Artist.objects.create(name='Nirvana', description='Legenda grunge')
        self.genre = Genre.objects.create(name='Rock')

    # --- 1. TEST MODELI ---
    def test_models_string_representation(self):
        """Sprawdza, czy modele poprawnie zwracają swoje nazwy (funkcja __str__)"""
        self.assertEqual(str(self.artist), 'Nirvana')
        self.assertEqual(str(self.genre), 'Rock')

    # --- 2. TEST WIDOKU PUBLICZNEGO ---
    def test_home_page_status_code_and_template(self):
        """Sprawdza, czy strona główna działa (kod 200) i używa dobrego szablonu"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/home.html')

    # --- 3. TEST ZABEZPIECZEŃ (Brak dostępu dla gościa) ---
    def test_add_cd_page_redirects_anonymous_user(self):
        """Sprawdza, czy niezalogowany gość zostanie wyrzucony ze strony dodawania płyty"""
        response = self.client.get(reverse('add_cd'))
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    # --- 4. TEST AUTORYZOWANEGO UŻYTKOWNIKA ---
    def test_add_cd_page_accessible_by_logged_in_user(self):
        """Sprawdza, czy zalogowany użytkownik ma normalny dostęp do dodawania płyty"""
        self.client.login(username='testuser', password='testpassword123')
        
        response = self.client.get(reverse('add_cd'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/add_cd.html')


# testy CRUD
class CDOfferCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='sprzedawca', password='password123')
        self.client.login(username='sprzedawca', password='password123')

        self.artist = Artist.objects.create(name='Pink Floyd')
        self.genre = Genre.objects.create(name='Rock')

        self.offer = CDOffer.objects.create(
            title='The Dark Side of the Moon',
            artist=self.artist,
            seller=self.user,
            price=50.00,
            condition='USED',
            description='Klasyk w dobrym stanie.'
        )
        self.offer.genres.add(self.genre)

    # --- CREATE ---
    def test_create_offer(self):
        """Testuje wysyłanie formularza (POST) dodającego nową płytę"""
        initial_count = CDOffer.objects.count()

        data = {
            'title': 'The Wall',
            'artist': self.artist.id,
            'new_artist': '',
            'genres': [self.genre.id],
            'new_genre': '',
            'price': 60.00,
            'condition': 'NEW',
            'description': 'Nowa w folii.'
        }

        response = self.client.post(reverse('add_cd'), data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

        self.assertEqual(CDOffer.objects.count(), initial_count + 1)
        self.assertTrue(CDOffer.objects.filter(title='The Wall').exists())

    # --- READ ---
    def test_read_offer_detail(self):
        """Testuje wczytywanie strony ze szczegółami konkretnej płyty"""
        response = self.client.get(reverse('offer_detail', args=[self.offer.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The Dark Side of the Moon')
        self.assertContains(response, '50.00')

    # --- UPDATE ---
    def test_update_offer(self):
        """Testuje formularz edycji istniejącego ogłoszenia"""
        data = {
            'title': 'The Dark Side of the Moon - Remastered',
            'artist': self.artist.id,
            'new_artist': '',
            'genres': [self.genre.id],
            'new_genre': '',
            'price': 55.00,
            'condition': 'USED',
            'description': 'Zaktualizowany opis.'
        }

        response = self.client.post(reverse('edit_cd', args=[self.offer.id]), data)
        self.assertEqual(response.status_code, 302)

        self.offer.refresh_from_db()

        self.assertEqual(self.offer.title, 'The Dark Side of the Moon - Remastered')
        self.assertEqual(self.offer.price, 55.00)

    # --- DELETE ---
    def test_delete_offer(self):
        """Testuje usunięcie ogłoszenia z bazy"""
        initial_count = CDOffer.objects.count()

        response = self.client.post(reverse('delete_cd', args=[self.offer.id]))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

        self.assertEqual(CDOffer.objects.count(), initial_count - 1)
        self.assertFalse(CDOffer.objects.filter(id=self.offer.id).exists())   


# --- TESTY WYSZUKIWARKI ---
class SearchTests(TestCase):
    def setUp(self):
        self.artist1 = Artist.objects.create(name='Nirvana')
        self.artist2 = Artist.objects.create(name='Pink Floyd')
        self.seller = User.objects.create_user(username='sprzedawca1', password='123')
        
        CDOffer.objects.create(title='Nevermind', artist=self.artist1, seller=self.seller, price=40, condition='USED', description='Test')
        CDOffer.objects.create(title='The Wall', artist=self.artist2, seller=self.seller, price=60, condition='NEW', description='Test')

    def test_search_by_title(self):
        """Sprawdza, czy wyszukiwarka poprawnie filtruje po tytule płyty"""
        response = self.client.get(reverse('home') + '?q=Never')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nevermind')
        self.assertNotContains(response, 'The Wall')

    def test_search_by_artist(self):
        """Sprawdza, czy wyszukiwarka poprawnie filtruje po wykonawcy"""
        response = self.client.get(reverse('home') + '?q=Floyd')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The Wall')
        self.assertNotContains(response, 'Nevermind')


# --- TESTY PROCESU TRANSAKCYJNEGO (KUPNO -> OPŁACENIE -> WYSYŁKA) ---
class OrderFlowTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(username='sprzedawca', password='123')
        self.buyer = User.objects.create_user(username='kupiec', password='123')
        
        self.artist = Artist.objects.create(name='Queen')
        self.offer = CDOffer.objects.create(
            title='A Night at the Opera', artist=self.artist, seller=self.seller, 
            price=100.00, condition='NEW', description='Nowa.'
        )

    def test_full_order_lifecycle(self):
        """Testuje cały cykl życia zamówienia: KUPNO -> OPŁACENIE -> WYSYŁKA"""
        
        self.client.login(username='kupiec', password='123')
        response_buy = self.client.post(reverse('buy_cd', args=[self.offer.id]))
        self.assertEqual(response_buy.status_code, 200)
        
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.buyer, self.buyer)
        self.assertEqual(order.status, 'PENDING')

        response_pay = self.client.post(reverse('pay_order', args=[order.id]))
        self.assertEqual(response_pay.status_code, 302)
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'PAID')

        self.client.login(username='sprzedawca', password='123')
        
        response_ship = self.client.post(reverse('ship_order', args=[order.id]))
        self.assertEqual(response_ship.status_code, 302)
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'SHIPPED')

    def test_buyer_cannot_ship_own_order(self):
        """Zabezpieczenie: Sprawdza, czy Kupujący nie może sam sobie 'wysłać' płyty"""
        order = Order.objects.create(cd=self.offer, buyer=self.buyer, status='PAID')
        
        self.client.login(username='kupiec', password='123')
        
        response = self.client.post(reverse('ship_order', args=[order.id]))
        
        self.assertEqual(response.status_code, 404)
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'PAID')