import mercadopago

public_key = "APP_USR-36d1ed4d-8501-4e68-b659-e2490032e56d"
token = "APP_USR-122134397188061-070109-173c510971bf6573849d8c94348f6543-1878501874"


def payment(order_items, link):
    
    sdk = mercadopago.SDK(token)

    items = []

    for item in order_items:
        quantity = int(item.amount)
        name = item.item_stock.item.name
        unit_price = float(item.item_stock.item.value)
        items.append({
            "title":name,
            "quantity":quantity,
            "unit_price":unit_price
        })

    preference_data = {
        "items": items,
        "back_urls": {
                "success":link,
                "pending":link,
                "failure":link
            }
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    payment_link = preference['sandbox_init_point']
    payment_id = preference['id']
    print(preference)
    return payment_link, payment_id