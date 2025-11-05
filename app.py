from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

app = Flask(__name__)

# Get OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Bakery menu with categories, prices, and image URLs
MENU = {
    "cakes": {
        "Chocolate Cake": {"price": 500, "image": "https://i.imgur.com/choco.jpg"},
        "Vanilla Cake": {"price": 450, "image": "https://i.imgur.com/vanilla.jpg"},
        "Red Velvet": {"price": 550, "image": "https://i.imgur.com/redvelvet.jpg"},
        "Custom Cake": {"price": 0, "image": ""}
    },
    "cupcakes": {
        "Choco Cupcake": {"price": 150, "image": "https://i.imgur.com/cupcakechoco.jpg"},
        "Vanilla Cupcake": {"price": 120, "image": "https://i.imgur.com/cupcakevanilla.jpg"}
    },
    "brownies": {
        "Fudge Brownie": {"price": 200, "image": "https://i.imgur.com/fudgebrownie.jpg"},
        "Nut Brownie": {"price": 220, "image": "https://i.imgur.com/nutbrownie.jpg"}
    },
    "pastries": {
        "Strawberry Pastry": {"price": 100, "image": "https://i.imgur.com/strawpastry.jpg"},
        "Cream Pastry": {"price": 120, "image": "https://i.imgur.com/creampastry.jpg"}
    }
}

# Track users' session and cart
user_sessions = {}

def format_menu():
    msg = "🍰 Krishna Bakery & Sweets Menu\n"
    for category, items in MENU.items():
        msg += f"\n*{category.title()}*\n"
        for name, details in items.items():
            price = details['price']
            msg += f"- {name}: ₹{price}\n"
    msg += "\nType your order like 'Chocolate Cake 2' or 'checkout' to finish."
    return msg

def get_ai_response(user_message):
    prompt = f"""
You are a friendly bakery assistant bot.
Customer message: "{user_message}"
- Greet if greeting.
- Show menu if asked.
- Give price, description, and image link if asking about any item.
- Suggest related items for upselling/cross-selling.
- Always respond professionally and politely.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("OpenAI Error:", e)
        return "Sorry, something went wrong. Please try again later."

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
                 "I can also help you place orders and answer bakery-related questions.")
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
                # Find price in MENU
                price = 0
                for cat_items in MENU.values():
                    if item['item'].lower() in map(str.lower, cat_items.keys()):
                        price = cat_items[item['item'].title()]['price']
                        break
                items_list += f"{item['quantity']} x {item['item']}\n"
                total += price * item['quantity']
            reply = (f"🛒 Your Order Summary:\n{items_list}"
                     f"Total: ₹{total}\nThank you for ordering at Krishna Bakery! 🙏")
            session['cart'] = []
    # Order handling
    else:
        parts = incoming_msg.split()
        qty = int(parts[-1]) if parts[-1].isdigit() else 1
        item_name = " ".join(parts[:-1]) if parts[-1].isdigit() else incoming_msg
        found = False
        for cat_items in MENU.values():
            for menu_item in cat_items.keys():
                if item_name.lower() == menu_item.lower():
                    session['cart'].append({"item": menu_item, "quantity": qty})
                    reply = (f"✅ Added {qty} x {menu_item} to your order.\n"
                             f"Current cart: {session['cart']}\nType 'checkout' to finish.")
                    # Upsell suggestion
                    suggestions = [i for i in cat_items.keys() if i.lower() != menu_item.lower()]
                    if suggestions:
                        reply += f"\nYou may also like: {', '.join(suggestions)}"
                    found = True
                    break
            if found:
                break
        if not found:
            reply = get_ai_response(incoming_msg)

    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
