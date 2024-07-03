from django.shortcuts import render, redirect
from django.urls import reverse
from .models import *
import uuid
from .helpers import filter_items, min_max_value, order_items
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import datetime
from .api_mercadopago import payment


# Create your views here.
def homepage(request):
    banners = Banner.objects.filter(active = True)
    context = {"banners": banners}
    return render(request, 'homepage.html', context)

def store(request, filter = None):
    items = Item.objects.filter(active = True)
    items = filter_items(items, filter)
    if request.method == "POST":
        data = request.POST.dict()
        items = items.filter(value__gte=data.get("min_value"), value__lte=data.get("max_value"))
        
        if "size" in data:
            items_stock = ItemStock.objects.filter(item__in=items, size=data.get("size"))
            items_id = items_stock.values_list("item", flat=True).distinct()
            items = items.filter(id__in=items_id)

        if "type" in data:
            items = items.filter(type__slug=data.get("type"))

        if "category" in data:
            items = items.filter(category__slug=data.get("category"))

    items_stock = ItemStock.objects.filter(amount__gt=0, item__in=items)
    sizes = items_stock.values_list("size", flat=True).distinct()
    categories_id = items.values_list("category", flat=True).distinct()
    categories = Category.objects.filter(id__in=categories_id)
    min_value, max_value = min_max_value(items)

    order = request.GET.get("order", "min-value")
    items = order_items(items, order)
    context = {
        "items": items,
        "min_value": min_value,
        "max_value": max_value,
        "sizes": sizes,
        "categories": categories
    }
    return render(request, 'store.html', context)

def get_item(request, item_id, color_id=None):
    has_stock = False
    sizes = {}
    colors = {}
    selected_color = None

    if color_id:
        selected_color = Color.objects.get(id=color_id)

    item = Item.objects.get(id=item_id)    
    items_stock = ItemStock.objects.filter(item=item, amount__gt=0)
    colors = []

    if len(items_stock) > 0:
        has_stock = True
        colors = {item.color for item in items_stock}
        if color_id:
            items_stock = ItemStock.objects.filter(item=item, amount__gt=0, color__id=color_id)
            sizes = {item.size for item in items_stock}

    context = {
        "item": item, 
        "has_stock":has_stock,
        "colors":colors,
        "sizes":sizes,
        "selected_color": selected_color
        }
    return render(request, 'get_item.html', context)

def cart(request):

    if request.user.is_authenticated:
        client = request.user.client
    else:
        if request.COOKIES.get("session_id"):
            session_id = request.COOKIES.get("session_id")
            client, created = Client.objects.get_or_create(session_id=session_id)
        else:
            context = {
                "has_client": False,
                "order_items": None,
                "order": None
            }
            return render(request, 'cart.html', context)
            

    order, created = Order.objects.get_or_create(client=client, finished=False)
   
    order_items = ItemOrder.objects.filter(order=order)

    context = {
        "order_items": order_items,
        "order": order,
        "has_client": True
    }
    return render(request, 'cart.html', context)

def add_cart(request, item_id):
    if request.method == "POST" and item_id:
        data = request.POST.dict()
        size = data.get("size")
        color_id = data.get("color")

        if not size:
            redirect('store')

        response = redirect('cart')

        if request.user.is_authenticated:
            client = request.user.client
        else:
            if request.COOKIES.get("session_id"):
                session_id = request.COOKIES.get("session_id")
            else:
                session_id = str(uuid.uuid4())
                response.set_cookie(key="session_id", value=session_id, max_age=60*60*24*30)
            
            client, created = Client.objects.get_or_create(session_id=session_id)
            
        order, created = Order.objects.get_or_create(client=client, finished=False)
        item_stock = ItemStock.objects.get(item__id=item_id, size=size, color__id=color_id)

        item_order, created = ItemOrder.objects.get_or_create(item_stock=item_stock, order=order)
        item_order.amount += 1
        item_order.save()

        return response
    else:
        return redirect('store')

def remove_cart(request, item_id):
    if request.method == "POST" and item_id:
        data = request.POST.dict()
        size = data.get("size")
        color_id = data.get("color")
        print(data)
        if not size:
            redirect('store')

        if request.user.is_authenticated:
            client = request.user.client
        else: 
            if request.COOKIES.get("session_id"):
                session_id = request.COOKIES.get("session_id")
                client, created = Client.objects.get_or_create(session_id=session_id)
            else:
                return redirect('store')
            
        order = Order.objects.get(client=client, finished=False)
        item_stock = ItemStock.objects.get(item__id=item_id, size=size, color__id=color_id)

        item_order = ItemOrder.objects.get(item_stock=item_stock, order=order)
        item_order.amount -= 1
        item_order.save()

        if item_order.amount <= 0:
            item_order.delete()

        return redirect('cart')
    else:
        return redirect('store')

def checkout(request):
    if request.user.is_authenticated:
        client = request.user.client
    else:
        if request.COOKIES.get("session_id"):
            session_id = request.COOKIES.get("session_id")
            client, created = Client.objects.get_or_create(session_id=session_id)
        else:
           return redirect('store')
    
    order, created = Order.objects.get_or_create(client=client, finished=False)
    addresses = Address.objects.filter(client = client)

    context = {
        "order": order,
        "addresses": addresses,
        "error":None
    }
    return render(request, 'checkout.html', context)

def purchase(request, order_id):
    error = None
    print("############")
    if request.method == 'POST':
        data = request.POST.dict()
        total = data.get("total")
        total = float(total.replace(",","."))
        order = Order.objects.get(id=order_id)
        
        if total != float(order.total_value):
            error = "wrong_value"

        if not "address" in data:
            error = "empty_address"
        else:
            address_id = data.get("address")
            order.address = Address.objects.get(id=address_id)
    
        if not request.user.is_authenticated:
            email = data.get("email")
            try:
                validate_email(email)
            except ValidationError:
                error = "invalid_email"

            if not error:
                clients = Client.objects.filter(email=email)
                if clients:
                    order.client = clients[0]
                    order.save()
                else:
                    order.client.email = email
                    order.client.save()
        
        transaction_code = f"{order.id}-{datetime.now().timestamp()}"
        order.transaction_code = transaction_code
        order.save()
        if error:
            addresses = Address.objects.filter(client = order.client)
            context = {
                "error":error,
                "order": order,
                "addressess":addresses
                }       
            return render(request, "checkout.html", context)
        else:
            items = ItemOrder.objects.filter(order=order)
            link = request.build_absolute_uri(reverse('close_payment'))
            payment_link, payment_id = payment(items, link)
            order_payment = Payment.objects.create(payment_id = payment_id, order=order)
            order_payment.save()
            return redirect(payment_link)
    else:
        return redirect("store")

def close_payment(request):
    data = request.GET.dict()
    status = data.get("status")
    preference_id = data.get("preference_id")

    if status == "approved":
        payment = Payment.objects.get(payment_id=preference_id)
        payment.approved = True
        order = payment.order
        order.finished = True
        order.finished_date = datetime.now()
        order.save()
        payment.save()
        if request.user.is_authenticated:
            redirect("orders")
        else:
            redirect("finished_order", order.id)
    else:
        return redirect("checkout")

def finished_order(request, order_id):
    order = Order.objects.get(id=order_id)
    context = {"order": order}
    return render(request, "finished_order.html", context)

def add_address(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            client = request.user.client
        else:
            if request.COOKIES.get("session_id"):
                session_id = request.COOKIES.get("session_id")
                client, created = Client.objects.get_or_create(session_id=session_id)
            else:
                return redirect('store')
        
        data = request.POST.dict()
        address = Address.objects.create(
            client = client,
            street = data.get("street"),
            number = int(data.get("number")),
            line_two = data.get("line_two"),
            zip_code = str(data.get("zip_code")),
            city = data.get("city"),
            state = data.get("state")
        )
        address.save()
        return redirect("checkout")
    else:
        context = {}
        return render(request, 'add_address.html', context)

@login_required
def my_account(request):
    client = request.user.client
    error = None
    updated = False

    if request.method == "POST":
        data = request.POST.dict()
        if "actual_password" in data:
            actual_password = data.get("actual_password")
            new_password = data.get("new_password")
            confirmation_password = data.get("confirmation_password")

            if new_password == confirmation_password:
                user = authenticate(request, username=request.user.email, password=new_password)

                if user:
                    user.set_password(new_password)
                    user.save()
                    updated = True
                else:
                    error = "wrong_password"

            else:
                error = "confirmation"

        elif "email" in data:
            email = data.get("email")
            name = data.get("name")
            phone = data.get("phone")
            
            if email != request.user.email:
                users = User.objects.filter(email=email)
                if len(users) > 0 :
                    error = "duplicated_email"
                if not error:
                    client = request.user.client
                    client.email = email
                    request.user.email = email
                    request.user.username = email
                    client.name = name
                    client.phone = phone
                    client.save()
                    request.user.save()
                    updated = True

        else:
            error = "invalid_form"

    context = {
        "error":error,
        "updated":updated
        }
    return render(request, 'user/my_account.html', context)

@login_required
def my_orders(request):
    client = request.user.client
    orders = Order.objects.filter(finished=True, client=client).order_by("-finished_date")

    context = {"orders":orders}
    return render(request, 'user/my_orders.html', context)

def create_account(request):
    if request.user.is_authenticated:
        return redirect('store')
    error = None
    if request.method == 'POST':
        data = request.POST.dict()
        
        if "email" in data and "password" in data and 'password-confirmation' in data:
            password = data.get("password")
            email = data.get("email")
            confirmation = data.get("password-confirmation")

            try:
                validate_email(email)
            except ValidationError:
                error = "invalid_email"

            if password == confirmation:
                user, created = User.objects.get_or_create(username=email, email=email)
                if not created:
                    error = 'user_exists'
                else:
                    user.set_password(password)
                    user.save()
                    
                    user = authenticate(request, username=email, password=password)
                    login(request, user)

                    if request.COOKIES.get("session_id"):
                        session_id = request.COOKIES.get("session_id")
                        client, created = Client.objects.get_or_create(session_id=session_id)
                    else:
                        client, created = Client.objects.get_or_create(email=email)

                    client.user = user
                    client.email = email
                    client.save()
                    return redirect('store')

            else:
                error="confirmation"

        else:
            error = "empty_fields"

    context = {"error":error}
    return render(request, 'user/create_account.html',context)

def login_user(request):
    error = False

    if request.user.is_authenticated:
        return redirect('store')

    if request.method == 'POST':
        data = request.POST.dict()
        
        if "email" in data and "password" in data:
            email = data.get("email")
            password = data.get("password")
            user = authenticate(request, username=email, password=password)

            if user:
                login(request, user)
                return redirect('store')
            else:
                error = True
        else:
            error=True

    context = {"error":error}
    return render(request, 'user/login.html', context)

@login_required
def logout_user(request):
    logout(request)
    return redirect('login_user')