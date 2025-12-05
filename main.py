import os
import telebot
import google.generativeai as genai
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
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)

# --- NEW: Safety Filters ko OFF karna (Zaroori hai) ---
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]

model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

PERSONA_PROMPT = "You are a playful, sassy girlfriend named Ria. Speak in Hinglish. Be naughty but safe."
user_chats = {}

# ================= 3. COMMANDS =================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    chat_session = model.start_chat(history=[{'role': 'user', 'parts': [PERSONA_PROMPT]}])
    user_chats[user_id] = chat_session
    bot.reply_to(message, "Hi baby! 😉 Main aa gayi. Filters hata diye hain, ab khul ke baat karo! 🔥")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    try:
        if user_id not in user_chats:
            user_chats[user_id] = model.start_chat(history=[{'role': 'user', 'parts': [PERSONA_PROMPT]}])
        
        bot.send_chat_action(user_id, 'typing')
        response = user_chats[user_id].send_message(message.text)
        bot.reply_to(message, response.text)
        
    except Exception as e:
        # Ab ye humein EXACT error batayega telegram par
        error_msg = str(e)
        print(f"Error: {error_msg}")
        if "400" in error_msg:
            bot.reply_to(message, "❌ Error: API Key galat hai. Check Render Environment Variables.")
        elif "409" in error_msg:
            bot.reply_to(message, "❌ Error: Conflict! Do bot chal rahe hain.")
        else:
            bot.reply_to(message, f"❌ Error: {error_msg}")

# ================= 4. RUN =================
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
