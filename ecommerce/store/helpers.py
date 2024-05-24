def filter_items(items, filter):
    if filter:
        if "-" in filter:
            category, type = filter.split("-")
            items = items.filter(type__slug=type, category__slug=category)
        else:
            items = items.filter(category__slug=filter)

    return items