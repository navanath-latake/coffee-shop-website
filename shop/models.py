from django.db import models 
from django.contrib.auth.models import User
# makemigrations-create changes and store in a file
# migration- apply the pending changes created by makemigrations

# Create your models here.
class Contact(models.Model):
    name=models.CharField(max_length=122)
    email=models.CharField(max_length=122)
    phone=models.CharField(max_length=12)
    desc=models.TextField()
    date=models.DateField()
    
    def _str_(self):
        return self.name  # + self.email

class Category(models.Model):
    name = models.CharField(max_length=255)
    def _str_(self):
        return self.name

class Product(models.Model):
    product_id=models.AutoField
    product_name=models.CharField(max_length=200)
    # category=models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    category=models.CharField(max_length=500)
    ingredients=models.CharField(max_length=2000,default="")
    description=models.TextField()
    price=models.DecimalField(max_digits=10,decimal_places=2) 
    image=models.ImageField(upload_to="house/images",default="")

    def _str_(self):
        return self.product_name

class Cart(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)

    def _str_(self):
        return f'Cart of {self.user.username}'

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)

    def _str_(self):
        return f'{self.quantity} of {self.product.product_name} in {self.cart.user.username}\'s cart'
    
    def total_price(self):
        return self.product.price*self.quantity
    
class Order(models.Model):
    STATUS_CHOICES=[
        ('PENDING','Pending'),
        ('ACCEPTED','Accepted'),
        ('REJECTED','Rejected'),
        ('DELIVERED','Delivered'),
    ]

    user=models.ForeignKey(User,on_delete=models.CASCADE)
    items=models.ManyToManyField(CartItem)
    total_price=models.DecimalField(max_digits=10,decimal_places=2)
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='PENDING')
    created_at=models.DateTimeField(auto_now=True)

    def _str_(self):
        return f'Order {self.id} by {self.user.username}'
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.orderitem_set.all())
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def _str_(self):
        return f'{self.quantity} of {self.product.product_name}'

    @property
    def total_price(self):
        return self.quantity * self.price


class Delivery(models.Model):
    order=models.OneToOneField(Order,on_delete=models.CASCADE)
    address = models.CharField(max_length=255 ,default="Default Address")
    city=models.CharField(max_length=100,default="Default city")
    state=models.CharField(max_length=100,default="Default state")
    postal_code=models.CharField(max_length=20,default="000000")
    delivered=models.BooleanField(default=False)
    delivery_time = models.DateTimeField(null=True,blank=True)
    delivered_at=models.DateTimeField(null=True,blank=True)

    def _str_(self):
        return f'Delivery for Order {self.order.id}'