def add_numbers(a, b):
    """Adds two numbers"""
    return a + b

def multiply_numbers(a, b):
    """Multiplies two numbers"""
    return a * b

def divide_numbers(a, b):
    """Divides a by b"""
    if b == 0:
        return "Error: Division by zero is not allowed"
    else:
        return a / b

print(add_numbers(2, 3))
print(multiply_numbers(4, 5))
print(divide_numbers(10, 2))