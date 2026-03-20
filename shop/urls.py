from django.urls import path
from shop import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name='shop'),
    path("about/", views.about, name='about'),
    path("services/", views.services, name='services'),
    path("contact/", views.contact, name='contact'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path("add_to_cart/<int:product_id>/", views.add_to_cart, name='add_to_cart'),
    path("view_cart/", views.view_cart, name='view_cart'),
    path("place_order/", views.place_order, name='place_order'),
    path("order/<int:order_id>/", views.order_detail, name='order_detail'),
    path('add_delivery/<int:order_id>/', views.add_delivery, name='add_delivery'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='shop/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('search/', views.search_products, name='search_products'),
]
