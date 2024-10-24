from django.urls import path
from .views import product_list, register, user_login, user_profile, city_list, district_list, area_list, neighborhood_list, create_address, add_to_cart, cart_view, clear_cart, payment_page, process_payment, mock, order_create

urlpatterns = [
    path('', product_list, name='product_list'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('profile/', user_profile, name='user_profile'),  # Ensure user_profile is imported
    path('api/cities/', city_list, name='city_list'),
    path('api/cities/<int:city_id>/districts/', district_list, name='district_list'),
    path('api/districts/<int:district_id>/areas/', area_list, name='area_list'),
    path('api/areas/<int:area_id>/neighborhoods/', neighborhood_list, name='neighborhood_list'),
    path('api/addresses/', create_address, name='create_address'),
    path('api/add-to-cart/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_view, name='cart_view'),
    path('api/clear-cart/', clear_cart, name='clear_cart'),
    path('add-to-cart/<int:product_id>/<int:price_id>/', add_to_cart, name='add_to_cart'),
    path('cart/payment', payment_page, name='payment_page'),
    path('cart/payment/process_payment/', process_payment, name='process_payment'),
    path('mock/', mock, name='mock'),
    path('api/order_create/', order_create, name='order_create'),
]
