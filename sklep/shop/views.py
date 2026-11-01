from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q
from .forms import CDOfferForm, CommentForm, CustomRegistrationForm
from .models import CDOffer, UserProfile, Order, Comment, CDImage, Genre, Artist

# Widok strony głównej
def home(request):
    offers = CDOffer.objects.filter(orders__isnull=True).order_by('-created_at')
    
    search_query = request.GET.get('q')
    
    if search_query:
        offers = offers.filter(
            Q(title__icontains=search_query) | Q(artist__name__icontains=search_query)
        )
    
    context = {
        'cds': offers,
        'search_query': search_query 
    }
    return render(request, "shop/home.html", context)


@login_required
def add_cd(request):
    if request.method == 'POST':
        form = CDOfferForm(request.POST, request.FILES)
        
        if form.is_valid():
            offer = form.save(commit=False)
            offer.seller = request.user
            
            # 1. Obsługa wykonawcy (wybrany lub nowy)
            new_artist_name = form.cleaned_data.get('new_artist')
            if new_artist_name:
                artist, created = Artist.objects.get_or_create(name=new_artist_name)
                offer.artist = artist
            
            offer.save()
            
            # 2. Obsługa gatunków (wybrane z listy)
            form.save_m2m() 
            
            # 3. Obsługa nowego gatunku
            new_genre_name = form.cleaned_data.get('new_genre')
            if new_genre_name:
                genre, created = Genre.objects.get_or_create(name=new_genre_name)
                offer.genres.add(genre)
            
            # 4. Obsługa wielu zdjęć
            images = request.FILES.getlist('images')
            for image in images:
                CDImage.objects.create(offer=offer, image=image)
            
            return redirect('home')
    else:
        form = CDOfferForm()
        
    return render(request, "shop/add_cd.html", {'form': form})
 
 
# Edycja oferty
@login_required
def edit_cd(request, pk):
    offer = get_object_or_404(CDOffer, pk=pk)
    
    if offer.seller != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = CDOfferForm(request.POST, request.FILES, instance=offer)
        
        if form.is_valid():
            form.save() 
            
            images = request.FILES.getlist('images')
            
            if images:
                offer.images.all().delete()
                
                # Zapisujemy nowe zdjęcia
                for image in images:
                    CDImage.objects.create(offer=offer, image=image)
                
            return redirect('offer_detail', pk=offer.pk)
    else:
        form = CDOfferForm(instance=offer)
        
    return render(request, "shop/edit_cd.html", {'form': form, 'offer': offer})
 
 
# Usuwanie oferty
@login_required
def delete_cd(request, pk):
    offer = get_object_or_404(CDOffer, pk=pk)
    if offer.seller != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        offer.delete()
        return redirect('home')
    return render(request, "shop/delete_cd.html", {'offer': offer})

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_offers = CDOffer.objects.filter(seller=profile_user, orders__isnull=True).order_by('-created_at')
    user_details, created = UserProfile.objects.get_or_create(user=profile_user)
    comments = user_details.received_comments.all().order_by('-created_at')

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.reviewed_profile = user_details
            new_comment.save()
            return redirect('user_profile', username=username)
    else:
        comment_form = CommentForm()

    context = {
        'profile_user': profile_user,
        'user_details': user_details,
        'offers': user_offers,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, "shop/profile.html", context)

# Rejestracja
def register(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            phone = form.cleaned_data.get('phone_number')
            address = form.cleaned_data.get('address')
            
            UserProfile.objects.create(user=user, phone_number=phone, address=address)
            
            login(request, user)
            return redirect('home')
    else:
        form = CustomRegistrationForm()
        
    return render(request, 'shop/register.html', {'form': form})

# Szczegóły konkretnej oferty
def offer_detail(request, pk):
    offer = get_object_or_404(CDOffer, pk=pk)
    
    return render(request, "shop/offer_detail.html", {'offer': offer})

@login_required
def buy_cd(request, id):
    offer = get_object_or_404(CDOffer, id=id)
    
    if offer.seller == request.user:
        return redirect('offer_detail', id=offer.id)

    if request.method == 'POST':
        Order.objects.create(
            cd=offer,
            buyer=request.user,
            status='PENDING'
        )
        return render(request, "shop/order_success.html", {'offer': offer})

    return render(request, "shop/buy_confirm.html", {'offer': offer})


# --- WIDOKI DLA PROCESU ZAKUPU I SPRZEDAŻY ---

@login_required
def my_purchases(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-order_date')
    return render(request, "shop/my_purchases.html", {'orders': orders})

@login_required
def pay_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user, status='PENDING')
    
    if request.method == 'POST':
        order.status = 'PAID'
        order.save()
        return redirect('my_purchases')
        
    return render(request, "shop/pay_order.html", {'order': order})

@login_required
def my_sales(request):
    orders = Order.objects.filter(cd__seller=request.user).order_by('-order_date')
    return render(request, "shop/my_sales.html", {'orders': orders})

@login_required
def ship_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, cd__seller=request.user, status='PAID')
    
    if request.method == 'POST':
        order.status = 'SHIPPED'
        order.save()
        
    return redirect('my_sales')