```python
def calculate_discounted_total(cart, discount=0):
    """
    Calculates total price after discount, taking into account item quantity.
    Ensures that the final total does not go below zero.
    """
    total = sum(item.get("price", 0) * item.get("qty", 1) for item in cart)
    total -= discount
    return max(total, 0)
```
