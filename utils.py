def calculate_discounted_total(cart, discount=0):
    """
    Calculates total price after discount, considering quantity of each item.
    """
    total = 0
    for item in cart:
        total += item["price"] * item.get("qty", 1)  # Multiply by qty
    total -= discount
    return total
```
