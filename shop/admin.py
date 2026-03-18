from django.contrib import admin
from shop.models import Contact,Product,Cart,CartItem,Order,Delivery,Category

# Register your models here.
admin.site.register(Contact)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Delivery)
# admin.site.register(category)