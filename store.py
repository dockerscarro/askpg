# store.py

import datetime
from typing import List, Dict

# --- Data Classes ---

class Product:
    def __init__(self, product_id: int, name: str, price: float, stock: int):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock

    def __repr__(self):
        return f"Product({self.product_id}, {self.name}, ${self.price}, stock={self.stock})"


class Customer:
    def __init__(self, customer_id: int, name: str, email: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.cart: List[CartItem] = []
        self.order_history: List[Order] = []

    def __repr__(self):
        return f"Customer({self.customer_id}, {self.name}, {self.email})"


class CartItem:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity

    def total_price(self):
        return self.product.price * self.quantity

    def __repr__(self):
        return f"CartItem({self.product.name}, qty={self.quantity})"


class Order:
    def __init__(self, order_id: int, customer: Customer, items: List[CartItem], order_date: datetime.datetime = None):
        self.order_id = order_id
        self.customer = customer
        self.items = items
        self.order_date = order_date or datetime.datetime.now()
        self.status = "Pending"

    def total_amount(self):
        return sum(item.total_price() for item in self.items)

    def __repr__(self):
        return f"Order({self.order_id}, {self.customer.name}, total=${self.total_amount():.2f}, status={self.status})"


# --- Store Management ---

class Store:
    def __init__(self):
        self.products: Dict[int, Product] = {}
        self.customers: Dict[int, Customer] = {}
        self.orders: Dict[int, Order] = {}
        self.next_order_id = 1

    # Product Management
    def add_product(self, product_id: int, name: str, price: float, stock: int):
        if product_id in self.products:
            raise ValueError(f"Product with id {product_id} already exists.")
        self.products[product_id] = Product(product_id, name, price, stock)

    def update_stock(self, product_id: int, quantity: int):
        if product_id not in self.products:
            raise ValueError("Product not found.")
        self.products[product_id].stock += quantity

    # Customer Management
    def add_customer(self, customer_id: int, name: str, email: str):
        if customer_id in self.customers:
            raise ValueError(f"Customer with id {customer_id} already exists.")
        self.customers[customer_id] = Customer(customer_id, name, email)

    # Cart Management
    def add_to_cart(self, customer_id: int, product_id: int, quantity: int):
        customer = self.customers.get(customer_id)
        product = self.products.get(product_id)
        if not customer or not product:
            raise ValueError("Customer or Product not found.")
        if quantity > product.stock:
            raise ValueError("Not enough stock available.")
        # Check if product already in cart
        for item in customer.cart:
            if item.product.product_id == product_id:
                item.quantity += quantity
                break
        else:
            customer.cart.append(CartItem(product, quantity))

    def remove_from_cart(self, customer_id: int, product_id: int):
        customer = self.customers.get(customer_id)
        if not customer:
            raise ValueError("Customer not found.")
        customer.cart = [item for item in customer.cart if item.product.product_id != product_id]

    def calculate_cart_total(self, customer_id: int, discount: float = 0.0):
        customer = self.customers.get(customer_id)
        if not customer:
            raise ValueError("Customer not found.")
        total = sum(item.total_price() for item in customer.cart)
        return max(total - discount, 0)

    # Order Management
    def place_order(self, customer_id: int, discount: float = 0.0):
        customer = self.customers.get(customer_id)
        if not customer:
            raise ValueError("Customer not found.")
        if not customer.cart:
            raise ValueError("Cart is empty.")
        order = Order(self.next_order_id, customer, customer.cart.copy())
        self.next_order_id += 1
        order_total = self.calculate_cart_total(customer_id, discount)
        self.orders[order.order_id] = order
        customer.order_history.append(order)
        # Reduce stock
        for item in customer.cart:
            item.product.stock -= item.quantity
        customer.cart.clear()
        return order, order_total

    def list_orders(self):
        return list(self.orders.values())

    def __repr__(self):
        return f"Store(Products={len(self.products)}, Customers={len(self.customers)}, Orders={len(self.orders)})"


# --- Example Usage ---
if __name__ == "__main__":
    store = Store()

    # Add some products
    store.add_product(1, "Laptop", 1200.0, 10)
    store.add_product(2, "Headphones", 150.0, 25)
    store.add_product(3, "Mouse", 25.0, 50)

    # Add a customer
    store.add_customer(101, "Alice", "alice@example.com")

    # Customer adds items to cart
    store.add_to_cart(101, 1, 1)
    store.add_to_cart(101, 3, 2)

    # Calculate cart total with discount
    total = store.calculate_cart_total(101, discount=50)
    print(f"Cart total after discount: ${total}")

    # Place an order
    order, order_total = store.place_order(101, discount=50)
    print(f"Placed Order: {order}")
    print(f"Order total after discount: ${order_total}")

    # Show all orders
    print("All orders:", store.list_orders())
