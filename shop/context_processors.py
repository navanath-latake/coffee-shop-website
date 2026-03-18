from .models import CartItem,Cart

def cart_quantity(request):
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            cart_quantity = CartItem.objects.filter(cart=cart).count()
        except Cart.DoesNotExist:
            cart_quantity = 0
    else:
        cart_quantity = 0

    return {'cart_quantity': cart_quantity}