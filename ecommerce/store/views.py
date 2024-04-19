from django.shortcuts import render
from .models import *

# Create your views here.
def homepage(request):
    banners = Banner.objects.all()
    context = {"banners": banners}
    return render(request, 'homepage.html', context)

def store(request):
    items = Item.objects.all()
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