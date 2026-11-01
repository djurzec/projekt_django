from django import forms
from .models import CDOffer, Comment, Artist, Genre
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# pozwala na wybór wielu plików w HTML
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# Obsługa listy plików
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class CDOfferForm(forms.ModelForm):
    images = MultipleFileField(
        widget=MultipleFileInput(attrs={'class': 'form-control'}),
        required=False,
        label="Zdjęcia płyty"
    )

    artist = forms.ModelChoiceField(
        queryset=Artist.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Wybierz z listy wykonawców"
    )
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        label="Wybierz gatunki z listy"
    )

    new_artist = forms.CharField(
        max_length=100, 
        required=False, 
        label="...albo wpisz nowego wykonawcę (zostanie dodany do bazy)", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wpisz nazwę wykonawcy'})
    )
    new_genre = forms.CharField(
        max_length=50, 
        required=False, 
        label="...albo wpisz nowy gatunek (zostanie dodany do bazy)", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wpisz nazwę gatunku'})
    )

    class Meta:
        model = CDOffer
        fields = ['title', 'artist', 'new_artist', 'genres', 'new_genre', 'price', 'condition', 'description']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Np. Dark Side of the Moon'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        artist = cleaned_data.get('artist')
        new_artist = cleaned_data.get('new_artist')
        
        # 1. Walidacja wykonawcy
        if artist and new_artist:
            self.add_error(None, 'Błąd: Nie możesz jednocześnie wybrać wykonawcy z listy i wpisać nowego. Zdecyduj się na jedną opcję.')
        elif not artist and not new_artist:
            self.add_error(None, 'Błąd: Musisz wybrać wykonawcę z listy lub wpisać nowego.')

        genres = cleaned_data.get('genres')
        new_genre = cleaned_data.get('new_genre')
        
        # 2. Walidacja gatunku
        if genres and new_genre:
            self.add_error(None, 'Błąd: Nie możesz jednocześnie wybrać gatunku z listy i wpisać nowego. Zdecyduj się na jedną opcję.')
        elif not genres and not new_genre:
            self.add_error(None, 'Błąd: Musisz wybrać gatunek z listy lub wpisać nowy.')

        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content'] 
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# --- FORMULARZ REJESTRACJI ---
class CustomRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=True, label="Numer telefonu")
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Np. ul. Fajna 1, 00-123 Warszawa'}), 
        required=True, 
        label="Pełny adres do wysyłki"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        
        phone = phone.replace(' ', '').replace('-', '')
        
        if not phone.isdigit():
            raise forms.ValidationError("Numer telefonu może zawierać tylko cyfry.")
        
        if len(phone) != 9:
            raise forms.ValidationError("Numer telefonu musi składać się z dokładnie 9 cyfr.")
            
        return phone