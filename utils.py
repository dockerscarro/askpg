def calculate_discounted_total(cart, discount=0):
    """
    Calculates total price after discount.

    Takes into account the quantity of each item
    and ensures the total is not negative.
    """
    total = sum(item.get("price", 0) * item.get("qty", 1) for item in cart)
    total -= discount
    return max(total, 0)  # Ensure total is not negative
```
These updates ensure that the quantity of each item is considered when calculating the total and prevent the total from being negative.
