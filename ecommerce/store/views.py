from django.shortcuts import render

# Create your views here.
def homepage(request):
    return render(request, 'homepage.html')

def store(request):
    return render(request, 'store.html')

def cart(request):
    return render(request, 'cart.html')

def checkout(request):
    return render(request, 'checkout.html')

def my_account(request):
    return render(request, 'user/my_account.html')

def login(request):
    return render(request, 'user/login.html')