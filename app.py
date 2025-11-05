from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Fixed bakery menu for greetings
BAKERY_MENU_TEXT = (
    "🍰 Menu:\n"
    "- Cakes\n"
    "- Cupcakes\n"
    "- Brownies\n"
    "- Pastries\n\n"
    "Type what you’d like to know about!"
)

# Example bakery items with prices
BAKERY_MENU = {
    "cupcakes": "$2 each",
    "chocolate cake": "$20 for 1kg",
    "vanilla cake": "$18 for 1kg",
    "brownies": "$3 each",
    "pastries": "$2.5 each"
}

@app.route("/message", methods=["POST"])
def message():
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()

    # If user says hi or hello, send fixed menu
    if incoming_msg in ["hi", "hello", "hey", "menu"]:
        resp.message(BAKERY_MENU_TEXT)
        return str(resp)

    try:
        # AI reply for bakery-specific queries
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful bakery assistant. "
                        "Answer questions about cakes, cupcakes, pastries, prices, and store timings. "
                        "Always be friendly and polite. "
                        "If someone asks about an item, give the price from the menu."
                    )
                },
                {"role": "user", "content": incoming_msg}
            ],
            max_tokens=150
        )
        reply = completion.choices[0].message.content
        resp.message(reply)

    except Exception as e:
        # Fallback: list menu with prices
        fallback_msg = "Hello! Here’s our bakery menu:\n"
        for item, price in BAKERY_MENU.items():
            fallback_msg += f"- {item.title()}: {price}\n"
        fallback_msg += "\nAsk me about any item or price!"
        resp.message(fallback_msg)
        print("OpenAI Error:", e)

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
