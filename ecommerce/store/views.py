from django.shortcuts import render, redirect
from .models import *

# Create your views here.
def homepage(request):
    banners = Banner.objects.filter(active = True)
    context = {"banners": banners}
    return render(request, 'homepage.html', context)

def store(request, category_name = None):
    items = Item.objects.filter(active = True)

    if category_name:
        items = items.filter(category__name=category_name)

    context = {"items": items}
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

    order, created = Order.objects.get_or_create(client=client, finished=False)
   
    order_items = ItemOrder.objects.filter(order=order)

    context = {
        "order_items": order_items,
        "order": order
    }
    return render(request, 'cart.html', context)

def add_cart(request, item_id):
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
            return redirect('store')
            
        order, created = Order.objects.get_or_create(client=client, finished=False)
        item_stock = ItemStock.objects.get(item__id=item_id, size=size, color__id=color_id)

        item_order, created = ItemOrder.objects.get_or_create(item_stock=item_stock, order=order)
        item_order.amount += 1
        item_order.save()

        return redirect('cart')
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
    return render(request, 'checkout.html')

def my_account(request):
    return render(request, 'user/my_account.html')

def login(request):
    return render(request, 'user/login.html')