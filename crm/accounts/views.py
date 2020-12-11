from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product, Customer, Order

# Decorators
from .decorators import unauthenticated_user, allowed_users, admin_only

# Class based forms
from .forms import OrderForm, CreateUserForm, CustomerForm

# Rapid form creators instead of using a class based form
from django.forms import inlineformset_factory, modelformset_factory

# extern library for filter
from .filters import OrderFilter

# Allows us to block pages when user is not logged.
from django.contrib.auth.decorators import login_required

# Group model from admin
from django.contrib.auth.models import Group

# Allows us to perform auth actions
from django.contrib.auth import authenticate, login, logout

# For displaying messages to the user
from django.contrib import messages


''' DECORATORS USED
Custom decoraters were implemented: 

    * @unauthenticated_user
    * @allowed_users(allowed_roles=['admin'])
    * @admin_only

These restrict views if user isn't admin or is not logged
'''


@unauthenticated_user
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            # Associating user with a group
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            messages.success(request, 'Account was created for ' + username)
            return redirect('login')
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


# decorator that blocks access to register when user is authenticated
@unauthenticated_user
def login_page(request):
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


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def user(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    orders_delivered = orders.filter(status='Delivered').count()
    orders_pending = orders.filter(status='Pending').count()
    context = {
        'orders': orders,
        'orders_delivered': orders_delivered,
        'orders_pending': orders_pending,
        'total_orders': total_orders
    }
    return render(request, 'accounts/user.html', context)


@login_required(login_url='login')
@admin_only
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
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'accounts/products.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    customer_orders = orders.count()

    filter = OrderFilter(request.GET, queryset=orders)
    orders = filter.qs

    context = {
        'customer': customer,
        'customer_orders': customer_orders,
        'orders': orders,
        'filter': filter
    }
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def create_order(request, pk):
    OrderFormSet = inlineformset_factory(
        Customer, Order, fields=('product', 'status'), extra=1)
    customer = Customer.objects.get(id=pk)
    form_set = OrderFormSet(queryset=Order.objects.none(), instance=customer)

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
@allowed_users(allowed_roles=['admin'])
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
@allowed_users(allowed_roles=['admin'])
def delete_order(request, pk):
    order = Order.objects.get(id=pk)

    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {
        'order': order
    }
    return render(request, 'accounts/delete.html', context)


def update_user(request, pk):
    customer = Customer.objects.get(id=pk)
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer/' + pk)
    context = {}
    return render(request, 'accounts/customer_form.html', context)
