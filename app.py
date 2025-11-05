from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bakery WhatsApp Chatbot is active!"

@app.route('/whatsapp', methods=['POST'])
def webhook():
    msg = request.form.get('Body').lower()
    response = MessagingResponse()
    reply = response.message()

    if 'cake' in msg:
        reply.body("🎂 We have Chocolate, Red Velvet, and Blueberry cakes! Want to order one?")
    elif 'menu' in msg:
        reply.body("🍰 Menu:\n- Cakes\n- Cupcakes\n- Brownies\n- Pastries\nType what you’d like to know about!")
    elif 'order' in msg:
        reply.body("🧾 Please type your order like:\n'1 Chocolate cake for tomorrow 5pm'")
    elif 'thanks' in msg or 'thank you' in msg:
        reply.body("💖 You’re most welcome! Sweet wishes from Glen’s Bakehouse 🍰")
    else:
        reply.body("👋 Hi! I’m your *Bakery Chatbot*. Type 'menu' to see what’s fresh today!")
    
    return str(response)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
