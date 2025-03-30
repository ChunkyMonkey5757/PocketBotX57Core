import os
import asyncio
import random
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Build bot
app = ApplicationBuilder().token(TOKEN).build()

# Signal settings
DEFAULT_DURATION = "3m"
CONFIDENCE_THRESHOLD = 70
SIGNAL_INTERVAL = (90, 120)  # seconds

# Trade duration logic
def get_trade_duration():
    choice = random.choices(["1m", "3m", "5m"], weights=[2, 5, 3])[0]
    return choice

# Confidence generator
def get_confidence():
    return random.randint(60, 100)

# Countdown system
async def send_countdown(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    duration = get_trade_duration()
    confidence = get_confidence()

    await context.bot.send_message(chat_id=chat_id, text=f"**Signal Incoming**\nConfidence: {confidence}%\nTrade Duration: {duration}")

    if confidence < CONFIDENCE_THRESHOLD:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Low confidence signal — trade cautiously.")

    for sec in reversed(range(6)):
        await context.bot.send_message(chat_id=chat_id, text=f"Entry in {sec} sec...")
        await asyncio.sleep(1)

    await context.bot.send_message(chat_id=chat_id, text="**TRADE NOW!**")

# Signal loop handler
async def start_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("PocketBotX57 Signal Engine: Tier 3 Activated.")

    while True:
        try:
            await send_countdown(context)
            cooldown = random.randint(*SIGNAL_INTERVAL)
            await asyncio.sleep(cooldown)
        except Exception as e:
            print(f"[ERROR] {e}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Error occurred. Restarting loop...")
            await asyncio.sleep(5)

# Bot start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("PocketBotX57 is alive. Send /signals to activate Tier 3 trading mode.")

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("signals", start_signals))

print("PocketBotX57: Tier 3 Engine Online")
app.run_polling()
