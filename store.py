def calculate_discounted_total(cart, discount=0):
    """
    Calculates the total price after discount.

    BUG: Ignores quantity of each item.
    """
    total = 0
    for item in cart:
        total += item["price"]  # ❌ Bug: should multiply by qty
    total -= discount
    return total



