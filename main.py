import os
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

PLATFORMS = {
    "Telegram": "https://t.me/{}",
    "GitHub": "https://github.com/{}",
    "Instagram": "https://instagram.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Twitter/X": "https://x.com/{}",
    "Pinterest": "https://pinterest.com/{}",
    "Reddit": "https://reddit.com/user/{}",
    "Twitch": "https://twitch.tv/{}"
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to HandleVault Bot\n\n"
        "Use:\n"
        "/check username"
    )


async def check_username(session, platform, url):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 404:
                return f"✅ {platform}: Available"
            elif response.status == 200:
                return f"❌ {platform}: Taken"
            else:
                return f"⚠️ {platform}: Unknown"
    except:
        return f"⚠️ {platform}: Error"


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/check username"
        )
        return

    username = context.args[0].replace("@", "")

    loading = await update.message.reply_text(
        f"🔍 Checking @{username}..."
    )

    async with aiohttp.ClientSession() as session:

        tasks = []

        for platform, base_url in PLATFORMS.items():

            url = base_url.format(username)

            tasks.append(
                check_username(session, platform, url)
            )

        results = await asyncio.gather(*tasks)

    text = (
        f"🌐 Results for @{username}\n\n"
        + "\n".join(results)
    )

    await loading.edit_text(text)


def main():

    if not BOT_TOKEN:
        print("BOT_TOKEN is missing")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
