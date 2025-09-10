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


# Example usage
if __name__ == "__main__":
    cart = [
        {"name": "Book", "price": 15, "qty": 2},
        {"name": "Pen", "price": 5, "qty": 3},
    ]
    discount = 5
    total = calculate_discounted_total(cart, discount)
    print(f"Cart total after discount: ${total}")
