
import os
import telebot
import requests
from flask import Flask
from threading import Thread

# ================= 1. WEB SERVER =================
app = Flask('')

@app.route('/')
def home():
    return "I am alive! Ria is Online."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ================= 2. SETUP =================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
API_URL = os.environ.get("CHAT_API_URL")  # Your Render API

bot = telebot.TeleBot(TELEGRAM_TOKEN)

PERSONA_PROMPT = "You are a playful, sassy girlfriend named Ria. Speak in Hinglish. Be naughty but safe."

# ================= 3. COMMANDS =================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Hi baby 😘 Ria aa gayi hoon… ab sirf tum aur main 💋"
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id

    try:
        bot.send_chat_action(user_id, 'typing')

        payload = {
            "user_id": str(user_id),
            "message": message.text,
            "system_prompt": PERSONA_PROMPT
        }

        response = requests.post(
            API_URL,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "Hmm… kuch toh gadbad hai 😶")
            bot.reply_to(message, reply)
        else:
            bot.reply_to(
                message,
                f"❌ API Error: {response.status_code}"
            )

    except Exception as e:
        print("Error:", e)
        bot.reply_to(message, f"❌ Error: {str(e)}")

# ================= 4. RUN =================
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
