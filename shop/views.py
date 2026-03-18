from django.shortcuts import render,get_object_or_404,redirect
from datetime import datetime
from shop.models import Contact
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Product,Cart,CartItem,Order,OrderItem,Delivery,Category
from .forms import DeliveryForm

# Create your views here.
def index(request):
    # return HttpResponse("This is Home page")
    context={
        'variable':"My name is pooja",
        'variable2':"pooja is great"
    }
    return render(request,'shop/index.html',context)

def about(request):
    return render(request,'shop/about.html')

def services(request):
    return render(request,'shop/services.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        contact = Contact(name=name, email=email, phone=phone, desc=desc, date=datetime.today())
        contact.save()
        messages.success(request, "Your message has been sent!")


    return render(request,'shop/contact.html')

@login_required
def add_to_cart(request,product_id):
    product=get_object_or_404(Product,id=product_id)
    cart, created=Cart.objects.get_or_create(user=request.user)
    cart_item, created=CartItem.objects.get_or_create(cart=cart,product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')

@login_required
def view_cart(request):
    cart, created=Cart.objects.get_or_create(user=request.user)
    cart_items=CartItem.objects.filter(cart=cart)
    total_price=sum(item.total_price() for item in cart_items)

    return render(request,'shop/view_cart.html',{'cart_items':cart_items,'total_price':total_price})

@login_required
def place_order(request):
    cart=get_object_or_404(Cart,user=request.user)
    cart_items=CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        return redirect('view_cart')
    
    order=Order.objects.create(user=request.user)

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
    
    cart_items.delete()
    return redirect('add_delivery', order_id=order.id)
    return redirect('order_detail',order_id=order.id)

    if request.method == 'POST':
        order=Order.objects.create(
            user=request.user,
            total_price=sum(item.total_price() for item in cart_items),
            status='PENDING'
        )
        order.items.set(cart_items)
        order.save()

        

    return render(request,'shop/place_order.html',{'cart_items':cart_items})
    
@login_required
def order_detail(request,order_id):
    order=get_object_or_404(Order,id=order_id,user=request.user)
    order_items=OrderItem.objects.filter(order=order)
    try:
        delivery = order.delivery
    except Delivery.DoesNotExist:
        delivery = None
    return render(request, 'shop/order_detail.html', {'order': order, 'order_items': order_items, 'delivery': delivery})

    if request.method == 'POST':
        action=request.POST.get('action')
        if action == 'accept' and order.status == 'PENDING':
            order.status='ACCEPTED'
            order.save()

        elif action == 'reject' and order.status=='PENDING':
            order.status='REJECTED'
            order.save()

        elif action == 'deliver' and order.status == 'ACCEPTED':
            order.status='DELIVERED'
            order.save()
            delivery=order.delivery
            delivery.delivered_at=timezone.now()
            delivery.save()
        return redirect('order_detail',order_id=order.id)
    return render(request,'shop/order_detail.html',{'order':order,'order_items':order_items,'delivery':delivery})

def product_list(request):
    products=Product.objects.all()
    return render(request,'shop/product_list.html',{'products':products})   

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def add_delivery(request, order_id):
    order=get_object_or_404(Order,id=order_id,user=request.user)
    if request.method == 'POST':
        form=DeliveryForm(request.POST)
        if form.is_valid():
            delivery =form.save(commit=False)
            delivery.order=order
            delivery.save()
            return redirect('order_detail',order_id=order.id)
    else:
        form=DeliveryForm()
    return render(request,'shop/add_delivery.html',{'form':form,'order':order})

def product_list_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'shop/product_list_by_category.html', {'category': category, 'products': products})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'shop/category_list.html', {'categories': categories})