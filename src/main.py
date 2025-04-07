import asyncio
from telegram.ext import Application, CommandHandler
from src.signal_engine.engine import SignalEngine
from src.config import TELEGRAM_BOT_TOKEN
import ccxt.async_support as ccxt
import pandas as pd

async def fetch_data(asset="BTC/USD"):
    exchange = ccxt.kraken()
    ohlcv = await exchange.fetch_ohlcv(asset, timeframe='1m', limit=50)
    await exchange.close()
    return pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

engine = SignalEngine()  # Single instance for state (weights)

async def signal_command(update, context):
    data = await fetch_data()
    signal = await engine.process_market_data("BTC/USD", data)
    if signal:
        price = data['close'].iloc[-1]
        msg = engine.format_signal_message(signal, price)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode='Markdown')

async def feedback_command(update, context, outcome: bool):
    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a signal ID (e.g., /won 12345)")
        return
    signal_id = context.args[0]
    await engine.process_feedback(signal_id, outcome)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Feedback recorded: {'win' if outcome else 'loss'} for {signal_id}")

app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("signal", signal_command))
app.add_handler(CommandHandler("won", lambda u, c: feedback_command(u, c, True)))
app.add_handler(CommandHandler("lost", lambda u, c: feedback_command(u, c, False)))
app.run_polling()