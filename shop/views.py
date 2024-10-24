from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Product, UserProfile, City, District, Area, Neighborhood, Address, Cart, Stock, CartItem, ProductPrice, PaymentOption, PaymentMethod, Order,OrderStatus
from .serializers import CitySerializer, DistrictSerializer, AreaSerializer, NeighborhoodSerializer, AddressSerializer, AddToCartSerializer, OrderSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import requests
from .forms import UserLoginForm, UserRegisterForm, UserProfileForm
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.db.models import Sum
from collections import defaultdict
from decimal import Decimal



# Retrieve all products and render the product list
def product_list(request):
    products = Product.objects.all()  # Retrieve all products
    context = {'products': products}  # Data to send to the template
    return render(request, 'product_list.html', context)  # Render the template


# Handle user registration
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('login')  # Redirect to the login page
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


# Handle user login
def user_login(request):
    if request.user.is_authenticated:
        return redirect('user_profile')  # Kullanıcı zaten giriş yaptıysa profil sayfasına yönlendir

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']  # E-posta adresini al
            password = form.cleaned_data['password']

            # Kullanıcıyı e-posta ile kimlik doğrulama
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)  # Kullanıcıyı oturum aç
                return redirect('user_profile')  # Giriş başarılıysa profil sayfasına yönlendir
            else:
                messages.error(request, 'E-posta veya şifre hatalı.')
    else:
        form = UserLoginForm()  # POST değilse formu oluştur

    return render(request, 'login.html', {'form': form})


# User profile view
@login_required
def user_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        # Update user profile
        profile_form = UserProfileForm(request.POST, instance=user_profile)  # Pass the instance for updating
        if profile_form.is_valid():
            profile_form.save()  # Save the updated profile

            # Optionally, you can handle address addition here as well.
            address_data = {
                'user_profile': user_profile.id,
                'city': request.POST.get('city'),
                'district': request.POST.get('district'),
                'area': request.POST.get('area'),
                'neighborhood': request.POST.get('neighborhood'),
                'address': request.POST.get('address'),
            }

            # Add address via API
            response = requests.post('http://127.0.0.1:8000/api/addresses/', json=address_data)
            if response.status_code == 201:
                messages.success(request, 'Your profile has been updated and address added!')
                return redirect('user_profile')
            else:
                messages.error(request, 'Failed to add address. Please try again.')
        else:
            messages.error(request, 'Failed to update profile. Please correct the errors.')

    else:
        profile_form = UserProfileForm(instance=user_profile)  # Populate form with existing profile data

    context = {
        'user_profile': user_profile,
        'addresses': user_profile.address_set.all(),
        'profile_form': profile_form,  # Pass the profile form to the template
    }
    return render(request, 'user_profile.html', context)


# API endpoint to list all cities
@api_view(['GET'])
def city_list(request):
    cities = City.objects.all()  # Retrieve all cities
    serializer = CitySerializer(cities, many=True)  # Serialize the cities
    return Response(serializer.data)  # Return JSON response


# API endpoint to list districts by city ID
@api_view(['GET'])
def district_list(request, city_id):
    districts = District.objects.filter(city_id=city_id)  # Filter districts by city ID
    serializer = DistrictSerializer(districts, many=True)  # Serialize the districts
    return Response(serializer.data)  # Return JSON response


# API endpoint to list areas by district ID
@api_view(['GET'])
def area_list(request, district_id):
    areas = Area.objects.filter(district_id=district_id)  # Filter areas by district ID
    serializer = AreaSerializer(areas, many=True)  # Serialize the areas
    return Response(serializer.data)  # Return JSON response


# API endpoint to list neighborhoods by area ID
@api_view(['GET'])
def neighborhood_list(request, area_id):
    neighborhoods = Neighborhood.objects.filter(area_id=area_id)  # Filter neighborhoods by area ID
    serializer = NeighborhoodSerializer(neighborhoods, many=True)  # Serialize the neighborhoods
    return Response(serializer.data)  # Return JSON response


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_address(request):
    if request.method == "POST":
        # Directly use request.data to get the parsed data
        data = request.data

        user_profile = get_object_or_404(UserProfile, user=request.user)  # Giriş yapmış kullanıcının profili

        # Address nesnesini oluştur
        address = Address.objects.create(
            user_profile=user_profile,
            name=data.get('name'),  
            city_id=data.get('city'),  # ForeignKey olarak city ID'sini geçin
            district_id=data.get('district'),  # ForeignKey olarak district ID'sini geçin
            area_id=data.get('area'),  # ForeignKey olarak area ID'sini geçin
            neighborhood_id=data.get('neighborhood'),  # ForeignKey olarak neighborhood ID'sini geçin
            address=data.get('address')  # Adresi geçin
        )

        return JsonResponse({"message": "Address created successfully"}, status=201)

    return JsonResponse({"error": "Invalid request"}, status=400)  # Hatalı istek durumunda dönen cevap


@api_view(['POST'])  # Bu kısım, sadece POST isteklerine izin verir
def add_to_cart(request, product_id, price_id):
    # POST isteği yapıldığını kontrol et
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        price = get_object_or_404(ProductPrice, id=price_id)
        quantity = int(request.POST.get('quantity', 1))  # Miktarı al veya varsayılan 1 olsun

        # Kullanıcıya ait bir sepet oluşturun veya mevcut olanı alın
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Sepete ekleme işlemini yapın
        cart.add_to_cart(product=product, payment_method=price.payment_method, product_price=price, quantity=quantity)

        return redirect('product_list')  # Ürün listesinin olduğu sayfaya geri dönün


def cart_view(request):
    # Kullanıcının sepetini al
    cart = request.user.carts.first()
    cart_items = cart.items.all() if cart else []

    # Eğer sepette ürün yoksa
    if not cart_items:
        return render(request, 'cart.html', {'error': 'Your cart is empty.'})

    # Sepetteki ürün bilgilerini hazırlama
    product_data = []
    for item in cart_items:
        product_data.append({
            'id': item.product.id,  # Ürün ID'sini ekleyin
            'name': item.product.name,
            'quantity': item.quantity,
            'total_price': str(item.total_price),  # Burada total_price'ı kullanıyoruz
            'currency_symbol': item.product_price.currency.symbol  # Para birimi simgesi
        })

    # Sepetin toplam tutarını hesapla
    total_value = cart.get_total_value()

    if request.method == 'POST':
        address_id = request.POST.get('address_id')

        if not address_id:
            # Adres seçilmemişse hata mesajı göster
            return render(request, 'cart.html', {
                'product_data': product_data,
                'cart': cart,
                'error': 'You must select an address to proceed with payment.'
            })

        # Kullanıcının mevcut adresini kullan
        address = Address.objects.get(id=address_id, user_profile=request.user.userprofile)

        # Siparişi oluştur
        order, created = Order.objects.get_or_create(
            user=request.user,
            cart=cart,
            defaults={
                'total_value': total_value,
                'order_status_id': 1,
                'is_paid': False,
                'address': address  # Adres bilgisini ekle
            }
        )

        context = {
            'cart': cart,
            'product_data': product_data,
            'order_id': order.id,  # Sipariş ID'si ödeme sayfasına yönlendirilecek
        }

        return render(request, 'payment.html', context)

    return render(request, 'cart.html', {'product_data': product_data, 'cart': cart})



@api_view(['POST'])
def clear_cart(request):
    if request.user.is_authenticated:
        # Login kullanıcılar için sepeti temizle
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
        return Response({"message": "Cart cleared"}, status=status.HTTP_200_OK)

    # Misafir kullanıcılar için session sepetini temizle
    request.session['cart'] = {}
    return Response({"message": "Session cart cleared"}, status=status.HTTP_200_OK)

def payment_page(request):
    user_orders = Order.objects.filter(user=request.user, is_paid=False)

    if not user_orders.exists():
        return render(request, 'payment.html', {'error': "Ödeme yapılacak bir sipariş yok."})

    cart = request.user.carts.first()
    cart_items = cart.items.all() if cart else []

    product_data = []
    for item in cart_items:
        product_data.append({
            'name': item.product.name,
            'quantity': item.quantity,
            'total_price': str(item.total_price),
            'currency_symbol': item.product_price.currency.symbol
        })

    payment_options = PaymentOption.objects.all()

    return render(request, 'payment.html', {
        'product_data': product_data,
        'payment_options': payment_options,
        'user_orders': user_orders
    })



def process_payment(request):
    order_id = request.POST.get('checkout_data')

    # Siparişi al
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return render(request, 'payment.html', {'error': 'Order not found.'})

    # Sepet bilgilerini al
    product_data = []
    for item in order.cart.items.all():
        product_data.append({
            'name': item.product.name,
            'quantity': item.quantity,
            'total_price': str(item.total_price),
            'currency_symbol': item.product_price.currency.symbol
        })

    # Ödeme yöntemlerini al
    payment_options = PaymentOption.objects.all()

    return render(request, 'payment.html', {
        'product_data': product_data,
        'payment_options': payment_options,
        'order_id': order.id
    })


def mock(request):
    return render(request, 'mock.html')

@api_view(['POST'])
def process_payment(request):
    if request.method == 'POST':
        checkout_data = request.POST.get('checkout_data')  # Burada sipariş ID'sini alıyoruz
        payment_option = request.POST.get('payment_option')

        # Siparişi bul ve işlemi tamamla
        try:
            order = Order.objects.get(id=checkout_data, user=request.user)
            order.is_paid = True  # Ödeme başarılı
            order.save()
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

        # Burada ödeme yöntemine göre yönlendirme yapılabilir
        return JsonResponse({'redirect_url': payment_option})  # Ödeme sayfasına yönlendirme
    return JsonResponse({'error': 'Invalid request'}, status=400)


@api_view(['POST'])
def order_create(request):
    user = request.user
    cart = user.carts.first()  # Kullanıcının ilk sepetini al, eğer yoksa None olur

    if not cart:
        return Response({"error": "No cart found for this user."}, status=status.HTTP_404_NOT_FOUND)

    # Adres ID'sini al
    address_id = request.data.get('address_id')
    total_value = request.data.get('total_value')
    items = request.data.get('items', [])

    # Adresin geçerli olup olmadığını kontrol et
    try:
        address = Address.objects.get(id=address_id, user_profile=user.userprofile)
    except Address.DoesNotExist:
        return Response({"error": "Address does not exist."}, status=status.HTTP_400_BAD_REQUEST)

    # Siparişi oluştur
    order = Order.objects.create(
        user=user,
        cart=cart,
        address=address,
        total_value=total_value,
        order_status_id=1,  # Varsayılan durumu ayarla
        is_paid=False  # Varsayılan ödeme durumu
    )

    return Response({"order_id": order.id}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def update_order_payment_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.is_paid = True  # Ödeme başarılı ise is_paid'i true yap
        order.save()
        return Response({"success": "Order payment status updated."}, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)