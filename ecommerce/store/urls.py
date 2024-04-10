from django.urls import path
from .views import *

urlpatterns = [
    path('', homepage, name="homepage"),
    path('store/', store, name="store"),
    path('account/', my_account, name="my_account"),
    path('login/', login, name="login"),
    path('cart/', cart, name="cart"),
    path('checkout/', checkout, name="checkout")
]
