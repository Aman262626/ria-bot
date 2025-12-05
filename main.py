import os
import telebot
import google.generativeai as genai
from flask import Flask
from threading import Thread
import time

# ================= 1. WEB SERVER (Bina soye chalne ke liye) =================
app = Flask('')

@app.route('/')
def home():
    return "I am alive! Ria is waiting for messages. 😉"

def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ================= 2. CONFIGURATION (Keys Render se uthayega) =================
# Keys hum Render ki settings me daalenge, code me nahi
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    print("Error: API Keys nahi mili! Render settings check karo.")

# ================= 3. GEMINI & BOT SETUP =================
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

PERSONA_PROMPT = """
You are a playful, sassy, and slightly adventurous girlfriend named 'Ria'.
You love teasing your partner (the user) and have a 'dangerous' sense of humor.
You speak in a mix of Hindi and English (Hinglish).
Keep your responses relatively short, engaging, and full of personality. Use emojis freely.
"""

user_chats = {}

# ================= 4. BOT COMMANDS =================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    chat_session = model.start_chat(history=[
        {'role': 'user', 'parts': [PERSONA_PROMPT]},
        {'role': 'model', 'parts': ['Okay baby, samajh gayi. Main Ria hoon. 😉 Let\'s chat!']}
    ])
    user_chats[user_id] = chat_session
    bot.reply_to(message, "Hiii baby! 😉 Finally aa gaye? Main wait hi kar rahi thi. Bolo kya plan hai? 🔥")

@bot.message_handler(commands=['pic'])
def send_image(message):
    chat_id = message.chat.id
    try:
        prompt_text = message.text.replace('/pic', '').strip()
        if not prompt_text:
            bot.reply_to(message, "Aise nahi baby, batao toh kaisi photo chahiye? Example: /pic beautiful girl in rain")
            return
        bot.send_chat_action(chat_id, 'upload_photo')
        image_url = f"https://image.pollinations.ai/prompt/{prompt_text.replace(' ', '%20')}"
        bot.send_photo(chat_id, image_url, caption="Ye lo, sirf tumhare liye! 😘")
    except Exception as e:
        bot.reply_to(message, "Uff, network issue hai shayad. Baad me try karna baby.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_message = message.text
    
    if user_id not in user_chats:
        chat_session = model.start_chat(history=[
             {'role': 'user', 'parts': [PERSONA_PROMPT]},
             {'role': 'model', 'parts': ['Ready to chat!']}
        ])
        user_chats[user_id] = chat_session

    try:
        bot.send_chat_action(user_id, 'typing')
        response = user_chats[user_id].send_message(user_message)
        bot.reply_to(message, response.text)
    except Exception:
        bot.reply_to(message, "Mera mood thoda off hai (API Error), thodi der baad baat karte hain.")

# ================= 5. START SYSTEM =================
if __name__ == "__main__":
    keep_alive() # Server start karega
    print("Bot is starting...")
    bot.infinity_polling() # Bot start karega
