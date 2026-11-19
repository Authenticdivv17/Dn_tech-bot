import os
import requests
from datetime import time
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # -1004345261505

def get_trending_news():
    try:
        r = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        ids = r.json()[:5]
        news = []
        for id in ids:
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json", timeout=10).json()
            if item and item.get('title'):
                title = item['title']
                link = item.get('url', f"https://news.ycombinator.com/item?id={id}")
                news.append(f"🔥 {title}\n👉 {link}")
        return news
    except:
        return []

async def post_daily_news(context: ContextTypes.DEFAULT_TYPE):
    news = get_trending_news()
    if not news:
        return
    message = "💻 *DnTech Enterprise | Daily Tech Update* 🚀\n\nTop Trending Tech News Today:\n\n"
    for i, n in enumerate(news, 1):
        message += f"*{i}.* {n}\n\n"
    message += "Follow | Learn | Earn | Grow\n#DnTechEnterprise #TechNews #AI"
    await context.bot.send_message(chat_id=int(CHANNEL_ID), text=message, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to DnTech Enterprise!\n\n"
        "I fit help you with:\n"
        "✅ Latest Tech News - type /news\n"
        "✅ AI Tools & Gadgets\n"
        "✅ Tech Business Ideas\n\n"
        "Just ask me anything about tech!"
    )

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Fetching trending news...")
    news = get_trending_news()
    if not news:
        await update.message.reply_text("No news now, try again later.")
        return
    msg = "💻 *Trending Tech News:*\n\n"
    for i, n in enumerate(news, 1):
        msg += f"*{i}.* {n}\n\n"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "ai" in text:
        reply = "🤖 AI na the biggest thing now! Tools like ChatGPT, Gemini, Claude dey help people work faster. You wan make I list best free AI tools for you?"
    elif "phone" in text or "gadget" in text or "iphone" in text or "samsung" in text:
        reply = "📱 For phones/gadgets, tell me your budget and wetin you wan use am for — gaming, camera, or business? I go recommend the best one."
    elif "money" in text or "earn" in text or "business" in text:
        reply = "💰 You fit earn with tech through: 1) Content creation 2) Selling gadgets 3) AI services 4) Learning coding. Which one you like make I explain?"
    elif "news" in text:
        await news_command(update, context)
        return
    elif "hello" in text or "hi" in text or "hey" in text:
        reply = "Hello Tech Family! 👋 How far? Ask me anything about tech, AI, or gadgets."
    else:
        reply = (
            "Good question! 💡\n\n"
            f"You ask about: '{update.message.text}'\n\n"
            "For now, I sabi Tech News, AI Tools, Gadgets & Tech Business. "
            "Try ask like: 'Best AI tools?' or type /news for trending news."
        )
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer_question))

    # Daily post by 9am Nigeria time (WAT = UTC+1)
    wat = pytz.timezone("Africa/Lagos")
    app.job_queue.run_daily(post_daily_news, time=time(hour=9, minute=0, tzinfo=wat))

    print("DnTech Bot is running 24/7...")
    app.run_polling()

if __name__ == "__main__":
    main()
