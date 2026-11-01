# Giełda Płyt CD

Nasz projekt to aplikacja internetowa typu e-commerce stworzona w frameworku Django, która umożliwia użytkownikom kupowanie oraz sprzedawanie płyt CD, zarządzanie swoimi ofertami, a także wystawianie opinii innym sprzedawcom.

## Główne funkcjonalności

Projekt realizuje pełny cykl życia ogłoszenia (CRUD) oraz proces transakcyjny:
* **Autoryzacja użytkowników:** Rejestracja, logowanie i wylogowywanie.
* **Zarządzanie ofertami (CRUD):** * Tworzenie nowych ogłoszeń (z możliwością dodania nowego wykonawcy/gatunku do bazy).
  * Odczyt szczegółów płyty wraz z przewijaną galerią zdjęć.
  * Edycja własnych ogłoszeń.
  * Usuwanie własnych ogłoszeń.
* **Galeria zdjęć:** Możliwość dodania wielu zdjęć do jednej oferty (obsługa formatów JPG/PNG).
* **System transakcyjny:** Kupowanie płyt z podziałem na statusy zamówienia (`Oczekujące`, `Opłacone`, `Wysłane`).
* **Panele użytkownika:** Dedykowane widoki "Moje zakupy" oraz "Moja sprzedaż" do śledzenia statusu transakcji.
* **System opinii:** Możliwość wystawiania publicznych komentarzy na profilach sprzedawców.
* **Wyszukiwarka:** Dynamiczne wyszukiwanie ofert po tytule płyty lub nazwie wykonawcy.

## Modele danych (Struktura bazy)

Projekt opiera się na 7 powiązanych ze sobą modelach danych:
1. **UserProfile:** Rozszerzenie domyślnego modelu użytkownika Django, przechowujące dodatkowe dane kontaktowe (telefon, adres).
2. **Artist:** Wykonawca lub zespół muzyczny (nazwa, opis).
3. **Genre:** Gatunek muzyczny (np. Rock, Pop).
4. **CDOffer:** Główny model ogłoszenia płyty, powiązany relacjami z wykonawcą, gatunkami oraz użytkownikiem (sprzedawcą). Przechowuje tytuł, cenę, stan płyty oraz opis.
5. **CDImage:** Model przechowujący zdjęcia. Posiada relację One-To-Many z ofertą (`CDOffer`), co pozwala na dodanie wielu zdjęć do jednej płyty.
6. **Order:** Model transakcji łączący kupującego z konkretną ofertą. Monitoruje status zamówienia (oczekujące na płatność, opłacone, wysłane).
7. **Comment:** System opinii pozwalający użytkownikom oceniać profile sprzedawców po udanych transakcjach.

## Wykorzystane technologie

* **Backend:** Python 3, Django
* **Baza danych:** SQLite (domyślna dla Django)
* **Frontend:** HTML5, Bootstrap 5 (system siatki, komponenty, karuzele)
* **Obsługa multimediów:** Biblioteka Pillow (do obsługi pól `ImageField`)

## Własne komendy zarządzające (manage.py)

Projekt zawiera autorskie polecenia ułatwiające zarządzanie portalem z poziomu terminala:

* `python manage.py add_genre <nazwa_gatunku>` – Błyskawiczne dodanie nowego gatunku muzycznego do bazy danych.
* `python manage.py export_offers` – Eksportuje listę wszystkich aktualnie dostępnych (niesprzedanych) płyt do pliku CSV (idealne do inwentaryzacji).
* `python manage.py shop_summary` – Wyświetla szybkie statystyki sklepu (liczba użytkowników, historia wszystkich wystawionych płyt, płyty dostępne obecnie do zakupu oraz liczba transakcji).

## Testy automatyczne

Aplikacja posiada zaimplementowane testy automatyczne weryfikujące poprawność działania modeli, widoków publicznych, zabezpieczeń przed dostępem osób niezalogowanych, pełnego systemu CRUD dla ofert, wyszukiwarki oraz cyklu życia zamówienia.

## Wykorzystanie AI
Wykorzystałyśmy sztuczną inteligencję głównie do tworzenia plików HTML, by móc skupić się na bardziej znaczących plikach projektu odpowiedzialnych za logikę. W przypadku jakichkolwiek błędów, napotkanych trudności albo braku pomysłu na dalsze działania również stosowałyśmy AI.

## Bibliografia i źródła
* **Oficjalna dokumentacja Django:** Oficjalna dokumentacja Django: Wykorzystana do implementacji modeli, widoków, formularzy oraz testów jednostkowych.

* **Gemini 3.1 Pro:** Wsparcie sztucznej inteligencji przy analizie błędów, generowaniu widoków HTML/Bootstrap. (Nazwa firmy: Google, data dostępu: marzec 2026)

* **Bootstrap 5 Documentation:** Wykorzystana do ostylowania frontendu aplikacji.

## Praca zespołowa
Członkowie grupy:
Katarzyna Dądera 
Dominika Jurzec 