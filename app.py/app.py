import os
from flask import Flask, request
import requests
import google.generativeai as genai

app = Flask(__name__)

# Tokens (Inhe variables me save karenge)
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN")  # Koi bhi khufia code rakh लें
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/', methods=['GET'])
def verify():
    # Facebook Webhook Verification
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == FB_VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello World", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"].get("text")
                    
                    if message_text:
                        # AI se answer lena
                        response = model.generate_content(message_text)
                        ai_reply = response.text
                        
                        # Reply bhejna
                        send_message(sender_id, ai_reply)
    return "ok", 200

def send_message(recipient_id, message_text):
    params = {"access_token": FB_PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
