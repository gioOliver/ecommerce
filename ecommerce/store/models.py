from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Client(models.Model):
    name        = models.CharField(max_length=200, null=True, blank=True)
    email       = models.CharField(max_length=200, null=True, blank=True)
    phone       = models.CharField(max_length=13, null=True, blank=True)
    session_id  = models.CharField(max_length=13, null=True, blank=True)
    user        = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.email)

class Category(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.name)

class Type(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return str(self.name)
    
class Item(models.Model):
    image       = models.ImageField(null=True, blank=True)
    name        = models.CharField(max_length=200, null=True, blank=True)
    value       = models.DecimalField(max_digits=10, decimal_places=2)
    active      = models.BooleanField(default=True)
    category    = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    type        = models.ForeignKey(Type, null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return f"Name: {self.name}, Category: {self.category}, Type: {self.type}, Price: {self.value}"

class Color(models.Model):
    name        = models.CharField(max_length=200, null=True, blank=True)
    code        = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class ItemStock(models.Model):
    item    = models.ForeignKey(Item, null=True, blank=True, on_delete=models.SET_NULL)
    color   = models.ForeignKey(Color, null=True, blank=True, on_delete=models.SET_NULL)
    size    = models.CharField(max_length=400, null=True, blank=True)
    amount  = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.item.name}, Tamanho: {self.size}, Cor: {self.color.name}"

class Address(models.Model):
    street      = models.CharField(max_length=400, null=True, blank=True)
    number      = models.IntegerField(default=0)
    line_two    = models.CharField(max_length=200, null=True, blank=True)
    zip_code    = models.CharField(max_length=200, null=True, blank=True)
    city        = models.CharField(max_length=200, null=True, blank=True)
    state       = models.CharField(max_length=200, null=True, blank=True)
    client      = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)

class Order(models.Model):
    client              = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    finished            = models.BooleanField(default=True)
    transaction_code    = models.CharField(max_length=400, null=True, blank=True)
    address             = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL)
    finished_date       = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Client: {self.client.email} - Id {self.id} - Finished: {self.finished}"

    @property
    def total_amount(self):
        items = ItemOrder.objects.filter(order__id=self.id)
        amount = sum( [item.amount for item in items] )
        return amount

    @property
    def total_value(self):
        items = ItemOrder.objects.filter(order__id=self.id)
        value = sum( [item.total_value for item in items] )
        return value

class ItemOrder(models.Model):
    item_stock  = models.ForeignKey(ItemStock, null=True, blank=True, on_delete=models.SET_NULL)
    amount      = models.IntegerField(default=0)
    order       = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)


    def __str__(self) -> str:
        return f"Order Id - {self.order.id} - Item: {self.item_stock.item}, {self.item_stock.size}, {self.item_stock.color.name}"

    @property
    def total_value(self):
        return self.amount * self.item_stock.item.value

class Banner(models.Model):
    image   = models.ImageField(null=True, blank=True)
    url     = models.CharField(max_length=400, null=True, blank=True)
    active  = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.url} - active: {self.active}"