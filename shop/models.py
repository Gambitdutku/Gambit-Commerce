from django.db import models
from django.contrib.auth.models import User

### Para Birimi Modeli ###
class Currency(models.Model):
    name = models.CharField(max_length=100)  # Para birimi adı
    symbol = models.CharField(max_length=4)  # Para birimi sembolü (USD, EUR vs.)

    def __str__(self):
        return self.name

### Ürün Modeli ###
class Product(models.Model):
    name = models.CharField(max_length=100)  # Ürün adı
    description = models.TextField()  # Ürün açıklaması
    image = models.ImageField(upload_to='products/')  # Ürün resmi

    def __str__(self):
        return self.name

### Ödeme Yöntemi Modeli ###
class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)  # Ödeme yöntemi adı (Kredi Kartı, Nakit vs.)

    def __str__(self):
        return self.name

### Ürün Fiyatı Modeli ###
class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Ürünle ilişkilendirilen fiyat
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)  # Fiyatın geçerli olduğu ödeme yöntemi
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)  # Fiyatın geçerli olduğu para birimi
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Fiyat

    def __str__(self):
        return f"{self.product.name} - {self.price} {self.currency.symbol}"

### Şehir Modeli ###
class City(models.Model):
    name = models.CharField(max_length=20, null=True)  # Şehir adı

    def __str__(self):
        return self.name

### İlçe Modeli ###
class District(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, related_name='districts')  # İlgili şehir
    name = models.CharField(max_length=20, null=True)  # İlçe adı

    def __str__(self):
        return self.name

### Alan Modeli (Semt/Mahalle gibi) ###
class Area(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, related_name='areas')  # İlgili şehir
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, related_name='areas')  # İlgili ilçe
    name = models.CharField(max_length=30, null=True)  # Alan/Semt adı

    def __str__(self):
        return self.name

### Mahalle Modeli ###
class Neighborhood(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, related_name='neighborhoods')  # İlgili şehir
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, related_name='neighborhoods')  # İlgili ilçe
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, related_name='neighborhoods')  # İlgili alan/semt
    name = models.CharField(max_length=90, null=True)  # Mahalle adı
    postal_code = models.CharField(max_length=5, null=True)  # Posta kodu

    def __str__(self):
        return self.name

### Kullanıcı Profili Modeli ###
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Kullanıcıyla birebir ilişki
    first_name = models.CharField(max_length=30)  # Kullanıcı adı
    last_name = models.CharField(max_length=30)  # Soyadı
    email = models.EmailField()  # E-posta
    phone_number = models.CharField(max_length=15)  # Telefon numarası
    birth_date = models.DateField()  # Doğum tarihi

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

### Adres Modeli ###
class Address(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # İlgili kullanıcı profili
    name = models.CharField(max_length=100, default="home")  # Adresin adı (örn. Ev, İş)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)  # Şehir
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True)  # İlçe
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)  # Alan/Semt
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE, null=True)  # Mahalle
    address = models.TextField(blank=True)  # Adres detayları

    def __str__(self):
        return f"{self.neighborhood.name}, {self.district.name}, {self.city.name}"

### Stok Modeli ###
class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='stock')  # Ürünle birebir ilişki
    quantity = models.PositiveIntegerField(default=0)  # Stok miktarı
    is_infinite = models.BooleanField(default=False)  # Sonsuz stok var mı

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"

### Sepet Modeli ###
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    def add_to_cart(self, product, payment_method, product_price, quantity=1):
        # Stok kontrolü
        stock = product.stock
        if not stock.is_infinite:
            if stock.quantity < quantity:
                raise ValueError(f"Not enough stock for {product.name}. Available: {stock.quantity}")

        # Sepet item'ı oluşturma ya da miktarını artırma
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            payment_method=payment_method,
            product_price=product_price,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        if not stock.is_infinite:
            stock.quantity -= quantity
            stock.save()

        return cart_item

    def get_total_value(self):
        # Sepet içindeki tüm ürünlerin toplam değerini hesapla
        total = sum(item.total_price for item in self.items.all())
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    product_price = models.ForeignKey(ProductPrice, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"

    @property
    def total_price(self):
        return self.quantity * self.product_price.price

class PaymentOption(models.Model):
    name = models.CharField(max_length=100)
    redirect_url = models.URLField()
    parameters = models.JSONField(default=list)

    def __str__(self):
        return self.name

class OrderStatus(models.Model):  # Durum modelini OrderStatus olarak adlandırdık
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')  # Kullanıcı ile ilişkilendirilmiş sipariş
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)  # Sepet ile birebir ilişki
    address = models.ForeignKey(Address, on_delete=models.CASCADE)  # Adres bilgisi
    total_value = models.DecimalField(max_digits=10, decimal_places=2)  # Toplam tutar
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, default=1)  # Durum alanını güncelledik
    created_at = models.DateTimeField(auto_now_add=True)  # Sipariş oluşturulma tarihi
    is_paid = models.BooleanField(default=False)  # Ödenmiş mi

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


    def __str__(self):
        return f"Order {self.id} by {self.user.username}"