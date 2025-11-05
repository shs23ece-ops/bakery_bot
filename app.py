from flask import Flask, request
import os
import openai
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return "WhatsApp Bakery Bot is running!"

@app.route("/message", methods=["POST"])
def message():
    incoming_msg = request.values.get("Body", "").strip()
    resp = MessagingResponse()

    if incoming_msg:
        try:
            # Call OpenAI API to generate reply
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": incoming_msg}],
                max_tokens=150
            )
            reply = completion['choices'][0]['message']['content']
            resp.message(reply)
        except Exception as e:
            # If OpenAI API fails, return an error message
            resp.message("Sorry, something went wrong. Please try again later.")
            print("OpenAI Error:", e)

    return str(resp)

if __name__ == "__main__":
    # Bind to Render port
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

    app.run(port=5000, debug=True)
