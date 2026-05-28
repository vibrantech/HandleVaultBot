# main.py

import os
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

PLATFORMS = {
    "Telegram": "https://t.me/{}",
    "GitHub": "https://github.com/{}",
    "Instagram": "https://www.instagram.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Twitter/X": "https://x.com/{}",
    "Pinterest": "https://www.pinterest.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Twitch": "https://www.twitch.tv/{}"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


async def check_platform(session, platform, url):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 404:
                return f"✅ {platform}: Available"
            elif response.status == 200:
                return f"❌ {platform}: Taken"
            else:
                return f"⚠️ {platform}: Unknown"
    except Exception:
        return f"⚠️ {platform}: Error"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Welcome to HandleVault Bot\n\n"
        "Check username availability across platforms.\n\n"
        "Usage:\n"
        "/check username\n\n"
        "Example:\n"
        "/check vibrant"
    )

    await update.message.reply_text(text)


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "⚠️ Please enter a username.\n\nExample:\n/check vibrant"
        )
        return

    username = context.args[0].replace("@", "").strip()

    if len(username) < 3:
        await update.message.reply_text(
            "❌ Username must be at least 3 characters long."
        )
        return

    loading = await update.message.reply_text(
        f"🔍 Checking @{username}..."
    )

    results = []

    async with aiohttp.ClientSession(headers=HEADERS) as session:

        tasks = []

        for platform, url in PLATFORMS.items():
            tasks.append(
                check_platform(
                    session,
                    platform,
                    url.format(username)
                )
            )

        responses = await asyncio.gather(*tasks)

        for result in responses:
            results.append(result)

    message = (
        f"🌐 Username Results For @{username}\n"
        f"━━━━━━━━━━━━━━━\n\n"
        + "\n".join(results)
    )

    await loading.edit_text(message)


def main():

    if not BOT_TOKEN:
        raise Exception("BOT_TOKEN environment variable not found.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))

    print("Bot Started Successfully")

    app.run_polling()


if __name__ == "__main__":
    main()
