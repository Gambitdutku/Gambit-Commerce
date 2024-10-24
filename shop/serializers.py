from rest_framework import serializers
from .models import City, District, Area, Neighborhood, Address,  CartItem, Product, PaymentMethod, ProductPrice, Cart, Order, OrderStatus

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'

class NeighborhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
        fields = '__all__'
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['user_profile', 'name', 'city', 'district', 'area', 'neighborhood', 'address']

    def create(self, validated_data):
        return Address.objects.create(**validated_data)
class AddToCartSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    payment_method_id = serializers.IntegerField(write_only=True)
    product_price_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(write_only=True, default=1)

    class Meta:
        model = CartItem
        fields = ['product_id', 'payment_method_id', 'product_price_id', 'quantity']

    def create(self, validated_data):
        user = self.context['request'].user
        product = Product.objects.get(id=validated_data['product_id'])
        payment_method = PaymentMethod.objects.get(id=validated_data['payment_method_id'])
        product_price = ProductPrice.objects.get(id=validated_data['product_price_id'])
        quantity = validated_data['quantity']

        # Kullanıcının aktif sepetini bul veya oluştur
        cart, created = Cart.objects.get_or_create(user=user)

        # Sepete ürün ekle
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            payment_method=payment_method,
            product_price=product_price,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['address', 'total_value', 'is_paid']  # is_paid dışarıdan gelmeyecek, varsayılan False olacak

    def create(self, validated_data):
        address = validated_data.pop('address')  # Adresi al
        cart = validated_data.pop('cart')  # Cart'ı al

        # Toplam tutarı cart'tan al
        total_value = cart.get_total_value()  # Sepetin toplam değerini al

        # Siparişi oluştur
        order = Order.objects.create(
            user=self.context['request'].user,
            cart=cart,
            address=address,
            total_value=total_value,
            order_status_id=1,  # Varsayılan order_status
            is_paid=False  # Varsayılan is_paid durumu
        )

        return order