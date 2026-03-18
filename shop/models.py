from django.db import models  
from django.contrib.auth.models import User 

# Create your models here. 

class Contact(models.Model): 
    name = models.CharField(max_length=122) 
    email = models.CharField(max_length=122) 
    phone = models.CharField(max_length=12) 
    desc = models.TextField() 
    date = models.DateField(auto_now_add=True)  # FIX: auto_now_add so no manual date needed
     
    def __str__(self):              # FIX: was _str_ (missing underscores)
        return self.name


class Category(models.Model): 
    name = models.CharField(max_length=255) 

    def __str__(self):              # FIX: was _str_
        return self.name


class Product(models.Model): 
    # FIX: product_id=models.AutoField was missing () — Django adds AutoField id automatically anyway
    product_name = models.CharField(max_length=200) 
    category = models.CharField(max_length=500) 
    ingredients = models.CharField(max_length=2000, default="") 
    description = models.TextField() 
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    image = models.ImageField(upload_to="house/images", default="") 

    def __str__(self):              # FIX: was _str_
        return self.product_name


class Cart(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE) 

    def __str__(self):              # FIX: was _str_
        return f'Cart of {self.user.username}'


class CartItem(models.Model): 
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1) 

    def __str__(self):              # FIX: was _str_
        return f'{self.quantity} of {self.product.product_name} in {self.cart.user.username}\'s cart'
     
    @property                       # FIX: should be a @property so it works as attribute in templates
    def total_price(self): 
        return self.product.price * self.quantity


class Order(models.Model): 
    STATUS_CHOICES = [ 
        ('PENDING',   'Pending'), 
        ('ACCEPTED',  'Accepted'), 
        ('REJECTED',  'Rejected'), 
        ('DELIVERED', 'Delivered'), 
    ] 

    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    items = models.ManyToManyField(CartItem, blank=True)  # FIX: added blank=True so order can be saved before items added
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # FIX: removed duplicate @property below — can't have field + property with same name
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING') 
    created_at = models.DateTimeField(auto_now_add=True)  # FIX: auto_now=True updates on every save; auto_now_add=True only sets on creation

    def __str__(self):              # FIX: was _str_
        return f'Order {self.id} by {self.user.username}'

    def get_total_price(self):      # FIX: renamed from total_price to avoid conflict with the field above
        return sum(item.total_price for item in self.orderitem_set.all())


class OrderItem(models.Model): 
    order = models.ForeignKey(Order, on_delete=models.CASCADE) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1) 
    price = models.DecimalField(max_digits=10, decimal_places=2) 
     
    def __str__(self):              # FIX: was _str_
        return f'{self.quantity} of {self.product.product_name}'

    @property 
    def total_price(self): 
        return self.quantity * self.price


class Delivery(models.Model): 
    order = models.OneToOneField(Order, on_delete=models.CASCADE) 
    address = models.CharField(max_length=255, default="Default Address") 
    city = models.CharField(max_length=100, default="Default city") 
    state = models.CharField(max_length=100, default="Default state") 
    postal_code = models.CharField(max_length=20, default="000000") 
    delivered = models.BooleanField(default=False) 
    delivery_time = models.DateTimeField(null=True, blank=True) 
    delivered_at = models.DateTimeField(null=True, blank=True) 

    def __str__(self):              # FIX: was _str_
        return f'Delivery for Order {self.order.id}'