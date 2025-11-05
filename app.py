from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
import re

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Bakery Menu & Prices
BAKERY_ITEMS = {
    "cakes": {
        "chocolate cake": {"price": 20, "unit": "per kg", "desc": "Rich chocolate cake with ganache."},
        "vanilla cake": {"price": 18, "unit": "per kg", "desc": "Soft vanilla sponge with cream."},
        "red velvet cake": {"price": 22, "unit": "per kg", "desc": "Classic red velvet with cream cheese frosting."}
    },
    "cupcakes": {
        "chocolate cupcake": {"price": 2, "unit": "each", "desc": "Mini chocolate delight."},
        "vanilla cupcake": {"price": 2, "unit": "each", "desc": "Vanilla cupcake with icing."},
        "strawberry cupcake": {"price": 2.5, "unit": "each", "desc": "Strawberry flavored cupcake."}
    },
    "brownies": {
        "classic brownie": {"price": 3, "unit": "each", "desc": "Fudgy classic brownie."},
        "walnut brownie": {"price": 3.5, "unit": "each", "desc": "Brownie with crunchy walnuts."}
    },
    "pastries": {
        "croissant": {"price": 2.5, "unit": "each", "desc": "Flaky buttery croissant."},
        "apple pastry": {"price": 3, "unit": "each", "desc": "Pastry with apple filling."}
    }
}

STORE_INFO = {
    "location": "123 Bakery Street, Sweet City",
    "timings": "Mon-Sun 8AM - 8PM",
    "contact": "+1234567890"
}

# Formatted Menu
def get_full_menu():
    menu_text = "🍰 *Our Bakery Menu:*\n"
    for category, items in BAKERY_ITEMS.items():
        menu_text += f"\n*{category.title()}*\n"
        for item, details in items.items():
            menu_text += f"- {item.title()}: ${details['price']} {details['unit']} | {details['desc']}\n"
    menu_text += "\nType the name of the item or category to know more!"
    return menu_text

# Find item/category info
def find_bakery_response(msg):
    msg = msg.lower()
    # Category lookup
    for category, items in BAKERY_ITEMS.items():
        if category in msg:
            reply = f"🍰 *{category.title()} Menu:*\n"
            for item, details in items.items():
                reply += f"- {item.title()}: ${details['price']} {details['unit']}\n"
            return reply
        # Individual item lookup
        for item, details in items.items():
            if item in msg:
                return f"🍰 {item.title()} is ${details['price']} {details['unit']}. {details['desc']}"
    
    # Quantity/order detection
    order_match = re.findall(r'(\d+)\s+([a-zA-Z ]+)', msg)
    if order_match:
        total = 0
        response = "🛒 Your Order:\n"
        for qty, item_name in order_match:
            item_name = item_name.strip()
            found = False
            for category_items in BAKERY_ITEMS.values():
                if item_name in category_items:
                    price = category_items[item_name]['price']
                    total += int(qty) * price
                    response += f"- {qty} x {item_name.title()} = ${int(qty) * price}\n"
                    found = True
            if not found:
                response += f"- {qty} x {item_name.title()} = Item not found\n"
        response += f"\n💰 Total: ${total}"
        return response
    return None

@app.route("/message", methods=["POST"])
def message():
    incoming_msg = request.values.get("Body", "").strip()
    resp = MessagingResponse()

    # Greetings or menu request
    if incoming_msg.lower() in ["hi", "hello", "hey", "menu"]:
        resp.message(get_full_menu())
        return str(resp)
    
    # Check bakery menu first
    bakery_reply = find_bakery_response(incoming_msg)
    if bakery_reply:
        resp.message(bakery_reply)
        return str(resp)
    
    # Store info queries
    if "location" in incoming_msg.lower():
        resp.message(f"📍 Our bakery is located at: {STORE_INFO['location']}")
        return str(resp)
    if "time" in incoming_msg.lower() or "open" in incoming_msg.lower():
        resp.message(f"⏰ Store timings: {STORE_INFO['timings']}")
        return str(resp)
    if "contact" in incoming_msg.lower() or "number" in incoming_msg.lower():
        resp.message(f"📞 Contact us at: {STORE_INFO['contact']}")
        return str(resp)

    # Fallback AI (only bakery-related)
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "You are a helpful bakery assistant. "
                    "Answer only bakery-related questions about items, prices, availability, and store info."
                )},
                {"role": "user", "content": incoming_msg}
            ],
            max_tokens=150
        )
        resp.message(completion.choices[0].message.content)
    except Exception as e:
        resp.message("Sorry, something went wrong. Here is our menu:\n" + get_full_menu())
        print("OpenAI Error:", e)

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
