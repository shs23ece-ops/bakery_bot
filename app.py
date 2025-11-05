from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Example bakery menu (used for fallback or quick replies)
BAKERY_MENU = {
    "cupcakes": "$2 each",
    "chocolate cake": "$20 for 1kg",
    "vanilla cake": "$18 for 1kg",
    "brownies": "$3 each",
    "croissants": "$2.5 each"
}

@app.route("/message", methods=["POST"])
def message():
    incoming_msg = request.values.get("Body", "").lower()
    resp = MessagingResponse()

    try:
        # Use OpenAI GPT to generate bakery-specific reply
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful bakery assistant. "
                        "Answer questions about cakes, cupcakes, pastries, prices, and store timings. "
                        "If someone asks about items, provide prices from the menu. "
                        "Always be friendly and polite."
                    )
                },
                {"role": "user", "content": incoming_msg}
            ],
            max_tokens=150
        )
        reply = completion.choices[0].message.content
        resp.message(reply)

    except Exception as e:
        # Fallback if OpenAI API fails
        fallback_msg = "Hello! Here’s our bakery menu:\n"
        for item, price in BAKERY_MENU.items():
            fallback_msg += f"- {item.title()}: {price}\n"
        fallback_msg += "\nVisit us or ask any bakery-related question!"
        resp.message(fallback_msg)
        print("OpenAI Error:", e)

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
