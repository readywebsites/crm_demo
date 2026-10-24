from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django_countries.fields import CountryField
from django.utils import timezone
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)  # Unique code for the coupon
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Discount amount
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Minimum amount required for coupon to be valid
    start_date = models.DateTimeField(default=timezone.now)  # Start date for coupon validity
    end_date = models.DateTimeField()  # End date for coupon validity
    is_active = models.BooleanField(default=True)  # Is the coupon currently active

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return (self.is_active and 
                now >= self.start_date and 
                now <= self.end_date and 
                self.discount_amount > 0)

    def apply_coupon(self, total_amount):
        if not self.is_valid():
            return total_amount  # Coupon is invalid, return the total amount unchanged
        
        # Check if the total amount meets the minimum purchase requirement
        if total_amount < self.min_purchase_amount:
            return total_amount

        # Apply the discount amount
        return max(total_amount - self.discount_amount, 0)


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    conversion_rate = models.DecimalField(max_digits=10, decimal_places=2)
    symbol = models.CharField(max_length=5)

    def __str__(self):
        return self.code
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)  # Added field for full name
    address = models.TextField(blank=True, null=True)
    customer_notes = models.TextField(blank=True, null=True, help_text="CRM notes on customer preferences or interactions")
    loyalty_points = models.PositiveIntegerField(default=0, help_text="CRM loyalty rewards points")

    def __str__(self):
        return self.name or self.user.username


# Signal to create or update user profile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        UserProfile.objects.get_or_create(user=instance)
    elif not instance.is_superuser and hasattr(instance, 'userprofile'):
        instance.userprofile.save()


class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Stock Keeping Unit / Inventory Code")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Retail price
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Wholesale / Acquisition cost")
    stock_quantity = models.PositiveIntegerField(default=25, help_text="Current physical units in stock")
    low_stock_threshold = models.PositiveIntegerField(default=5, help_text="Threshold for low inventory alert")
    stock = models.BooleanField(default=True, help_text="Active for retail sale")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.sku or 'No SKU'})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

    def save(self, *args, **kwargs):
        if not self.sku:
            import random
            self.sku = f"SKU-{random.randint(10000, 99999)}"
        self.stock = (self.stock_quantity > 0)
        super().save(*args, **kwargs)
    
    def get_price(self, currency):
        if currency == 'USD':
            return self.price
        else:
            # Convert price to the selected currency using the conversion rate
            try:
                target_currency = Currency.objects.get(code=currency)
                converted_price = self.price * Decimal(target_currency.conversion_rate)
                return converted_price.quantize(Decimal('0.01'))  # Format to 2 decimal places
            except Currency.DoesNotExist:
                return None

    def get_absolute_url(self):
        return reverse('product_details', args=[str(self.id)])


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Image for {self.product.name}"


class Cart(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    products = models.ManyToManyField(Product, through='CartProduct')

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Cart with session {self.session_id}"

    def get_total_price(self):
        total = sum(item.product.price * item.quantity for item in self.cartproduct_set.all())
        return total

    def count_unique_items(self):
        unique_items_count = self.cartproduct_set.count()  # Count all CartProduct instances
        return unique_items_count
    

class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in {self.cart}"
    

class Wishlist(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'session_id', 'product')


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address_line_1 = models.CharField(max_length=255)
    country = CountryField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)  # New field for phone number
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.address_line_1},{self.country},{self.state},{self.city},{self.zipcode},{self.phone}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderProduct')
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Added total_price field
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    payment_status = models.CharField(max_length=20, choices=[
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ], default='unpaid')
    payment_method = models.CharField(max_length=100, default='Cash on Delivery / In-Store Pickup')
    order_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.user.username}"

    def get_total_price(self):
        total = sum(op.product.price * op.quantity for op in self.orderproduct_set.all())
        return total
    
    def get_invoice_number(self):
        return f"SM{self.pk:05d}"
    
    def formatted_created_at(self):
        return self.created_at.strftime('%d.%m.%Y')


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in order {self.order.id}"