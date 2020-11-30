from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product, Customer, Order

# Class based forms
from .forms import OrderForm, CreateUserForm

# Rapid form creators instead of using a class based form
from django.forms import inlineformset_factory, modelformset_factory

# extern library for filter
from .filters import OrderFilter

# Allows us to block pages when user is not logged.
from django.contrib.auth.decorators import login_required

# Allows us to perform auth actions
from django.contrib.auth import authenticate, login, logout

# For displaying messages to the user
from django.contrib import messages

def register(request):

    # Blocks access to register when user is authenticated
    if request.user.is_authenticated:
        return redirect('home')
    
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('login')
    context = { 'form': form }
    return render(request, 'accounts/register.html', context)

def login_page(request):
    # Blocks access to register when user is authenticated
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')
    context = {}
    return render(request, 'accounts/login.html', context)

def logout_user(request):
    logout(request)
    return redirect('login')

# This decorator restricts pages to users that aren't logged
@login_required(login_url='login')
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    total_customers = customers.count()
    total_orders = orders.count()
    orders_delivered = orders.filter(status='Delivered').count()
    orders_pending = orders.filter(status='Pending').count()

    context = {
        'orders': orders,
        'customers': customers,
        'total_orders': total_orders,
        'orders_delivered': orders_delivered,
        'orders_pending': orders_pending,
    }

    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
def products(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'accounts/products.html', context)

@login_required(login_url='login')
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    customer_orders = orders.count()

    filter = OrderFilter(request.GET, queryset = orders)
    orders = filter.qs

    context = {
        'customer': customer,
        'customer_orders': customer_orders,
        'orders': orders,
        'filter': filter
    }
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
def create_order(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=1)
    customer = Customer.objects.get(id=pk)
    form_set = OrderFormSet(queryset=Order.objects.none(),instance=customer)

    if request.method == 'POST':
        form_set = OrderFormSet(request.POST, instance=customer)
        if form_set.is_valid():
            form_set.save()
            return redirect('/')

    context = {
        'form_set': form_set,
        'customer': customer
    }
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
def update_order(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    
    context = {
        'form': form
    }
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
def delete_order(request, pk):
    order = Order.objects.get(id=pk)    

    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {
        'order': order
    }
    return render(request, 'accounts/delete.html', context)