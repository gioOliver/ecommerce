from .models import Order, ItemOrder, Client, Category, Type

def cart(request):

    cart_items_count = 0

    if request.user.is_authenticated:
        client = request.user.client
    else:
        if request.COOKIES.get("session_id"):
            session_id = request.COOKIES.get("session_id")
            client, created = Client.objects.get_or_create(session_id=session_id)
        else:
            return {"cart_items_count":cart_items_count}

    order, created = Order.objects.get_or_create(client=client, finished=False)
   
    order_item = ItemOrder.objects.filter(order=order)

    for item in order_item:
        cart_items_count += item.amount 

    return {
        "cart_items_count":cart_items_count
    }

def categories_types(request):
    categories = Category.objects.all()
    types = Type.objects.all()
    return {
        "categories": categories,
        "types": types
    }
