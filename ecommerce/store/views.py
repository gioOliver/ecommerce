from django.shortcuts import render
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

def cart(request):
    return render(request, 'cart.html')

def checkout(request):
    return render(request, 'checkout.html')

def my_account(request):
    return render(request, 'user/my_account.html')

def login(request):
    return render(request, 'user/login.html')