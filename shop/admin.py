from django.contrib import admin
from .models import (
    Currency, Cart, CartItem, Product, PaymentMethod, ProductPrice, City,
    District, Area, Neighborhood, UserProfile, Address, Stock, PaymentOption,
    Order, OrderStatus
)

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol')
    search_fields = ('name', 'symbol')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'payment_method', 'currency', 'price')
    search_fields = ('product__name', 'payment_method__name', 'currency__name')
    list_filter = ('currency', 'payment_method')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    search_fields = ('name', 'city__name')
    list_filter = ('city',)

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'district')
    search_fields = ('name', 'city__name', 'district__name')
    list_filter = ('city', 'district')

@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'postal_code', 'city', 'district', 'area')
    search_fields = ('name', 'postal_code', 'city__name', 'district__name', 'area__name')
    list_filter = ('city', 'district', 'area')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'phone_number', 'birth_date')
    search_fields = ('user__username', 'first_name', 'last_name', 'email')
    list_filter = ('birth_date',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'name', 'city', 'district', 'neighborhood')
    search_fields = ('user_profile__user__username', 'city__name', 'district__name', 'neighborhood__name')
    list_filter = ('city', 'district', 'neighborhood')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'is_infinite')
    search_fields = ('product__name',)
    list_filter = ('is_infinite',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'cart', 'payment_method', 'product_price')
    search_fields = ('product__name', 'cart__user__username')
    list_filter = ('payment_method', 'product_price')

@admin.register(PaymentOption)
class PaymentOption(admin.ModelAdmin):
    list_display = ('name', 'redirect_url')
    search_fields = ('name', 'redirect_url')

class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # OrderStatus'ların listeleneceği alanlar

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_value', 'order_status', 'created_at', 'is_paid')  # Siparişlerin listeleneceği alanlar
    list_filter = ('order_status', 'created_at', 'user')  # Filtreleme seçenekleri
    search_fields = ('user__username',)

admin.site.register(OrderStatus, OrderStatusAdmin)  # OrderStatus modelini admin paneline ekleyin
admin.site.register(Order, OrderAdmin)  # Sipariş modelini admin paneline ekleyin