from .models import Order, ItemOrder

def cart(request):

    cart_items_count = 0

    if request.user.is_authenticated:
        client = request.user.client
    else:
        return {"cart_items_count":cart_items_count}

    order, created = Order.objects.get_or_create(client=client, finished=False)
   
    order_item = ItemOrder.objects.filter(order=order)

    for item in order_item:
        cart_items_count += item.amount 

    return {
        "cart_items_count":cart_items_count
    }