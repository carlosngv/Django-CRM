from django.urls import path
from .views import main, products, customer

urlpatterns = [
    path('home', main),
    path('products', products),
    path('customer', customer)    
]