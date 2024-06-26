from django.urls import path
from .views import *

urlpatterns = [
    path('', homepage, name="homepage"),
    path('store/', store, name="store"),
    path('store/<str:filter>', store, name="store"),
    path('item/<int:item_id>/', get_item, name="get_item"),
    path('item/<int:item_id>/<int:color_id>', get_item, name="get_item"),
    path('cart/', cart, name="cart"),
    path('checkout/', checkout, name="checkout"),
    path('add-cart/<int:item_id>/', add_cart, name="add_cart" ),
    path('remove-cart/<int:item_id>/', remove_cart, name="remove_cart" ),
    path('add-address', add_address, name="add_address"),

    path('account/', my_account, name="my_account"),
    path('login/', login_user, name="login_user"),
    path('logout/', logout_user, name="logout_user"),
    path('create-account/', create_account, name="create_account")
]
