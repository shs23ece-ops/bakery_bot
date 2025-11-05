from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Bakery Menu with prices
MENU = {
    "cakes": {"Chocolate Cake": 500, "Vanilla Cake": 450, "Red Velvet Cake": 600},
    "cupcakes": {"Chocolate Cupcake": 100, "Vanilla Cupcake": 90, "Strawberry Cupcake": 120},
    "brownies": {"Fudge Brownie": 150, "Nut Brownie": 180},
    "pastries": {"Croissant": 80, "Danish": 70}
}

# To store user orders temporarily
user_orders = {}

def format_menu():
    menu_text = "🍰 *Krishna Bakery & Sweets Menu* 🍰\n\n"
    for category, items in MENU.items():
        menu_text += f"*{category.capitalize()}*\n"
        for item, price in items.items():
            menu_text += f"- {item}: ₹{price}\n"
        menu_text += "\n"
    menu_text += "Type the item name to order.\n"
    menu_text += "Type 'checkout' to finish your order."
    return menu_text

@app.route("/message", methods=["POST"])
def message():
    incoming_msg = request.values.get("Body", "").strip().lower()
    from_number = request.values.get("From")

    if from_number not in user_orders:
        user_orders[from_number] = []

    resp = MessagingResponse()
    msg = resp.message()

    # Greeting
    if incoming_msg in ["hi", "hello", "hey"]:
        msg.body("Hi! I am Krishna Bakery & Sweets chatbot 🍰. Type 'menu' to see our offerings.")
        return str(resp)

    # Show menu
    if incoming_msg == "menu":
        msg.body(format_menu())
        return str(resp)

    # Checkout order
    if incoming_msg == "checkout":
        if user_orders[from_number]:
            total = sum([MENU[item_category][item_name] for item_category, item_name in user_orders[from_number]])
            order_summary = "Your order:\n"
            for category, item in user_orders[from_number]:
                order_summary += f"- {item} ({category})\n"
            order_summary += f"Total: ₹{total}\nThank you for ordering! 🎉"
            msg.body(order_summary)
            user_orders[from_number] = []  # Clear order
        else:
            msg.body("You have no items in your order. Type 'menu' to see our bakery items.")
        return str(resp)

    # Check if incoming message matches menu items
    found = False
    for category, items in MENU.items():
        for item_name in items:
            if incoming_msg == item_name.lower():
                user_orders[from_number].append((category, item_name))
                msg.body(f"Added {item_name} to your order. 🛒\nType 'menu' to see more items or 'checkout' to finish.\nTip: Try our {category} specials for a combo offer!")
                found = True
                break
        if found:
            break

    if not found:
        msg.body("Sorry! I can only answer about our bakery items. Type 'menu' to see our offerings.")

    return str(resp)

if __name__ == "__main__":
    # Render assigns port dynamically via environment variable
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
