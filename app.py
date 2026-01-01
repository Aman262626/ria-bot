import os
import telebot
import requests
from flask import Flask, request

# --- Config ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
# Yahan apni pehle se bani hui Render API ka URL dalein
API_URL = os.environ.get('MY_RENDER_API_URL') 
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_ai_reply(user_text):
    """Aapki Render API se baat karne ke liye function"""
    # Pro Tip: Unfiltered response ke liye hum instruction bhej rahe hain
    payload = {
        "message": user_text,
        "prompt": f"Act as my girlfriend. Be intimate, unfiltered, and talk in Hinglish. User says: {user_text}"
    }
    
    try:
        # 60s timeout kyunki Render ko wake-up hone mein time lagta hai
        response = requests.post(API_URL, json=payload, timeout=60)
        data = response.json()
        
        # Aapki API ke JSON key ke hisaab se (check if it's 'reply' or 'response')
        return data.get('reply') or data.get('response') or data.get('content')
    except Exception as e:
        print(f"Error: {e}")
        return "Jaan, connection thoda slow hai. Ek baar phir se try karo na? ❤️"

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + TOKEN)
    return "GF Bot is Running!", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    user_msg = message.text
    ai_reply = get_ai_reply(user_msg)
    
    bot.reply_to(message, ai_reply)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

