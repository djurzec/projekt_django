from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views
 
urlpatterns = [
    path('', views.home, name='home'), 
    path('dodaj/', views.add_cd, name='add_cd'),
    path('oferta/<int:pk>/', views.offer_detail, name='offer_detail'),
    path('oferta/<int:pk>/edytuj/', views.edit_cd, name='edit_cd'),
    path('oferta/<int:pk>/usun/', views.delete_cd, name='delete_cd'),
    path('profil/<str:username>/', views.user_profile, name='user_profile'),
    path('oferta/<int:id>/kup/', views.buy_cd, name='buy_cd'),
    path('rejestracja/', views.register, name='register'),
    path('logowanie/', auth_views.LoginView.as_view(template_name='shop/login.html'), name='login'),
    path('wyloguj/', auth_views.LogoutView.as_view(), name='logout'),
    path('moje-zakupy/', views.my_purchases, name='my_purchases'),
    path('zamowienie/<int:order_id>/oplac/', views.pay_order, name='pay_order'),
    path('moja-sprzedaz/', views.my_sales, name='my_sales'),
    path('zamowienie/<int:order_id>/wyslij/', views.ship_order, name='ship_order'),
]
 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)