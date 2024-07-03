from django.contrib import admin
from .models import *

admin.site.register(Client)
admin.site.register(Category)
admin.site.register(Type)
admin.site.register(Item)
admin.site.register(ItemStock)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(ItemOrder)
admin.site.register(Banner)
admin.site.register(Color)
admin.site.register(Payment)