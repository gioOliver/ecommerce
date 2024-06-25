from django.db.models import Max, Min

def filter_items(items, filter):
    if filter:
        if "-" in filter:
            category, type = filter.split("-")
            items = items.filter(type__slug=type, category__slug=category)
        else:
            items = items.filter(category__slug=filter)

    return items

def min_max_value(items):
    min_value = 0
    max_value = 0
    if len(items) > 0:
        min_value = list(items.aggregate(Min("value")).values())[0]
        min_value = round(min_value, 2)
        max_value = list(items.aggregate(Max("value")).values())[0]
        max_value = round(max_value, 2)

    return min_value, max_value

def order_items(items, order):
    
    if order == "min-value":
        items = items.order_by("value")
    elif order == "max-value":
        items = items.order_by("-value")
    elif order == "best-seller":
        items_list = []
        for item in items:
            items_list.append((item.total_sales(), item))
        items_list = sorted(items_list, key=lambda x: x[0], reverse=True)
        items = [item[1] for item in items_list]
    return items