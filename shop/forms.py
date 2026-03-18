from django import forms
from .models import Order,Delivery
# class OrderForm(forms.ModelForm):
#     class Meta:
#         model=Order
#         fields=['items','total_price']

class DeliveryForm(forms.ModelForm):
    class Meta:
        model=Delivery
        fields=['address','city','state','postal_code']