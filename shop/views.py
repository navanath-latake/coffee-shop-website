from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Product, Cart, CartItem, Order, OrderItem, Delivery, Category, Contact
from .forms import DeliveryForm
from django.http import JsonResponse

# Create your views here.

def index(request):
    return render(request, 'shop/index.html')  # FIX: removed unused context variables


def about(request):
    return render(request, 'shop/about.html')


def services(request):
    return render(request, 'shop/services.html')


def contact(request):
    if request.method == "POST":
        name  = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc  = request.POST.get('desc')
        # FIX: Contact is imported from .models not shop.models separately
        # FIX: removed date=datetime.today() — model uses auto_now_add=True now
        contact_obj = Contact(name=name, email=email, phone=phone, desc=desc)
        contact_obj.save()
        messages.success(request, "Your message has been sent!")
        return redirect('contact')  # FIX: added redirect after POST to avoid resubmission

    return render(request, 'shop/contact.html')


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    cart_quantity = CartItem.objects.filter(cart=cart).count()

    # AJAX request → return JSON (no page reload)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f"{product.product_name} added to cart!",
            'cart_quantity': cart_quantity,
        })

    # Normal request → redirect back to referring page
    messages.success(request, f"{product.product_name} added to cart!")
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('product_list')


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items   = CartItem.objects.filter(cart=cart)
    # FIX: total_price is a @property now, so call without ()
    total_price  = sum(item.total_price for item in cart_items)

    return render(request, 'shop/view_cart.html', {
        'cart_items':  cart_items,
        'total_price': total_price
    })


@login_required
def place_order(request):
    cart       = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")  # FIX: added message
        return redirect('view_cart')

    if request.method == 'POST':  # FIX: only create order on POST, not on GET
        # FIX: calculate total before deleting cart items
        total = sum(item.total_price for item in cart_items)

        order = Order.objects.create(
            user=request.user,
            total_price=total,
            status='PENDING'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()  # FIX: clear cart after order is created

        return redirect('add_delivery', order_id=order.id)
        # FIX: removed the unreachable second return redirect below it
        # FIX: removed the entire dead if request.method=='POST' block that was after a return

    return render(request, 'shop/place_order.html', {'cart_items': cart_items})


@login_required
def order_detail(request, order_id):
    order       = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    try:
        delivery = order.delivery
    except Delivery.DoesNotExist:
        delivery = None

    # FIX: moved POST handling BEFORE the return so it actually executes
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'accept' and order.status == 'PENDING':
            order.status = 'ACCEPTED'
            order.save()
            messages.success(request, "Order accepted.")

        elif action == 'reject' and order.status == 'PENDING':
            order.status = 'REJECTED'
            order.save()
            messages.warning(request, "Order rejected.")

        elif action == 'deliver' and order.status == 'ACCEPTED':
            order.status = 'DELIVERED'
            order.save()
            if delivery:
                delivery.delivered     = True
                delivery.delivered_at  = timezone.now()
                delivery.save()
            messages.success(request, "Order marked as delivered.")

        return redirect('order_detail', order_id=order.id)

    return render(request, 'shop/order_detail.html', {
        'order':       order,
        'order_items': order_items,
        'delivery':    delivery
    })


def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})


@login_required
def add_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            delivery       = form.save(commit=False)
            delivery.order = order
            delivery.save()
            messages.success(request, "Delivery details saved!")  # FIX: added feedback
            return redirect('order_detail', order_id=order.id)
    else:
        form = DeliveryForm()

    return render(request, 'shop/add_delivery.html', {'form': form, 'order': order})


def product_list_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    # FIX: category field is CharField in Product, so filter by name not object
    products = Product.objects.filter(category=category.name)
    return render(request, 'shop/product_list_by_category.html', {
        'category': category,
        'products': products
    })


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'shop/category_list.html', {'categories': categories})


def search_products(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'results': []})
    
    products = Product.objects.filter(
        product_name__icontains=q
    ).values('id', 'product_name', 'price', 'category')[:8]
    
    return JsonResponse({'results': list(products)})

def remove_from_cart(request, item_id):
    CartItem.objects.filter(id=item_id).delete()
    return redirect('view_cart')


def increase_cart(request, item_id):
    item = CartItem.objects.get(id=item_id)
    item.quantity += 1
    item.save()
    return redirect('view_cart')

def decrease_cart(request, item_id):
    item = CartItem.objects.get(id=item_id)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()  # removes item if quantity hits 0
    return redirect('view_cart')
