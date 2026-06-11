import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NAN_API_KEY = os.getenv("NAN_API_KEY")

client = OpenAI(
    api_key=NAN_API_KEY,
    base_url="https://api.nan.builders/v1"
)

logging.basicConfig(level=logging.INFO)

async def manejar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text

    respuesta = client.chat.completions.create(
        model="qwen3.6",
        messages=[
            {"role": "system", "content": "Eres un asistente útil, claro y técnico."},
            {"role": "user", "content": texto}
        ],
        max_tokens=500
    )

    await update.message.reply_text(respuesta.choices[0].message.content)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar))

    print("Bot funcionando...")
    app.run_polling()