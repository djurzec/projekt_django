import os
from django.db import models
from django.contrib.auth.models import User

# 1. Profil Użytkownika
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

# 2. Wykonawca / Zespół
class Artist(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# 3. Gatunek Muzyczny
class Genre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# 4. Oferta Płyty CD
class CDOffer(models.Model):
    CONDITION_CHOICES = [
        ('NEW', 'Nowa'),
        ('USED', 'Używana'),
    ]
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='cds')
    genres = models.ManyToManyField(Genre, related_name='cds')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.artist.name}"
    
# 5. Zdjęcia do ofert
class CDImage(models.Model):
    # Relacja OneToMany - jedna oferta może mieć wiele zdjęć
    offer = models.ForeignKey(CDOffer, on_delete=models.CASCADE, related_name='images')
    # Używamy ImageField z biblioteki Pillow
    image = models.ImageField(upload_to='cd_images/')

    def __str__(self):
        return f"Zdjęcie do oferty: {self.offer.title}"
    

# 6. Zamówienie / Transakcja
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Oczekujące'),
        ('PAID', 'Opłacone'),
        ('SHIPPED', 'Wysłane'),
    ]
    cd = models.ForeignKey(CDOffer, on_delete=models.CASCADE, related_name='orders')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Zamówienie {self.id} - {self.cd.title}"

# 7. Komentarz / Opinia o sprzedawcy
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='written_comments')
    reviewed_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Opinia od {self.author.username} dla {self.reviewed_profile.user.username}"