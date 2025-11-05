from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Bakery menu with categories and prices
MENU = {
    "cakes": {
        "Chocolate Cake": 500,
        "Vanilla Cake": 450,
        "Red Velvet": 550,
        "Custom Cake": 0
    },
    "cupcakes": {
        "Choco Cupcake": 150,
        "Vanilla Cupcake": 120
    },
    "brownies": {
        "Fudge Brownie": 200,
        "Nut Brownie": 220
    },
    "pastries": {
        "Strawberry Pastry": 100,
        "Cream Pastry": 120
    }
}

# Track user session
user_sessions = {}

def format_menu():
    msg = "🍰 Krishna Bakery & Sweets Menu\n"
    for category, items in MENU.items():
        msg += f"\n*{category.title()}*\n"
        for name, price in items.items():
            msg += f"- {name}: ₹{price}\n"
    msg += "\nType 'checkout' to finish your order."
    return msg

@app.route("/message", methods=["POST"])
def message():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')

    resp = MessagingResponse()

    if from_number not in user_sessions:
        user_sessions[from_number] = {"cart": []}

    session = user_sessions[from_number]

    # Greeting
    if incoming_msg.lower() in ["hi", "hello", "hey"]:
        reply = ("Hi! I am Krishna Bakery & Sweets Chatbot 🍰.\n"
                 "You can view our menu by typing 'menu'. "
                 "I can also help you place orders.")
    # Show menu
    elif "menu" in incoming_msg.lower():
        reply = format_menu()
    # Checkout
    elif "checkout" in incoming_msg.lower():
        if not session['cart']:
            reply = "Your cart is empty! Type 'menu' to see our products."
        else:
            total = 0
            items_list = ""
            for item in session['cart']:
                item_name = item['item']
                qty = item['quantity']
                price = 0
                for cat_items in MENU.values():
                    if item_name in cat_items:
                        price = cat_items[item_name]
                        break
                items_list += f"{qty} x {item_name}\n"
                total += price * qty
            reply = (f"🛒 Your Order Summary:\n{items_list}"
                     f"Total: ₹{total}\nThank you for ordering at Krishna Bakery! 🙏")
            session['cart'] = []
    # Add item to cart
    else:
        parts = incoming_msg.split()
        qty = int(parts[-1]) if parts[-1].isdigit() else 1
        item_name = " ".join(parts[:-1]) if parts[-1].isdigit() else incoming_msg
        found = False
        for cat_items in MENU.values():
            for menu_item in cat_items.keys():
                if item_name.lower() == menu_item.lower():
                    session['cart'].append({"item": menu_item, "quantity": qty})
                    reply = f"✅ Added {qty} x {menu_item} to your order."
                    found = True
                    break
            if found:
                break
        if not found:
            reply = "Sorry, I didn't understand. Type 'menu' to see our products."

    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
