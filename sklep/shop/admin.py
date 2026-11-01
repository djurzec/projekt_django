from django.contrib import admin
from .models import Artist, Genre, CDOffer # Możesz od razu dodać CDOffer

admin.site.register(Artist)
admin.site.register(Genre)
admin.site.register(CDOffer)