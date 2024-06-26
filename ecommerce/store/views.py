from django.shortcuts import render, redirect
from .models import *
import uuid
from .helpers import filter_items, min_max_value, order_items
from django.contrib.auth import login, logout, authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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
        "addresses": addresses
    }
    return render(request, 'checkout.html', context)

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

def my_account(request):
    return render(request, 'user/my_account.html')

def create_account(request):
    if request.user.is_authenticated:
        return redirect('store')
    
    if request.method == 'POST':
        data = request.POST.dict()
        error = None

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


    return render(request, 'user/create_account.html')

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
