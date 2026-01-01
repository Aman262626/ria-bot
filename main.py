import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# ---------- AI RESPONSE ----------
def get_ai_reply(message):
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a sweet, caring, romantic girlfriend. "
                    "You talk in Hinglish and English. "
                    "You are emotional, supportive, and kind. "
                    "NO sexual or adult content. Keep it wholesome and loving."
                )
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    try:
        r = requests.post(
            "https://chatbot-ji1z.onrender.com/chatbot-ji1z",
            json=payload,
            timeout=15
        )
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Aww 🥺 thoda sa issue aa gaya, phir se try karo na 💛"


# ---------- BOT HANDLER ----------
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = get_ai_reply(user_message)
    await update.message.reply_text(response)


# ---------- START BOT ----------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    app.run_polling()


if __name__ == "__main__":
    main()
