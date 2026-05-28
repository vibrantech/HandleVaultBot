import os
import logging
import asyncio
import aiohttp

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# LOGGING
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

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
        "/check username\n\n"
        "Example:\n"
        "/check vibrant"
    )


async def check_platform(session, platform, url):

    try:

        async with session.get(url, timeout=10) as response:

            if response.status == 404:
                return f"✅ {platform}: Available"

            elif response.status == 200:
                return f"❌ {platform}: Taken"

            else:
                return f"⚠️ {platform}: Unknown"

    except Exception as e:

        logger.error(f"{platform} error: {e}")

        return f"⚠️ {platform}: Error"


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:

        await update.message.reply_text(
            "Usage:\n/check username"
        )

        return

    username = context.args[0].replace("@", "").strip()

    loading = await update.message.reply_text(
        f"🔍 Checking @{username}..."
    )

    results = []

    async with aiohttp.ClientSession() as session:

        tasks = []

        for platform, base_url in PLATFORMS.items():

            url = base_url.format(username)

            tasks.append(
                check_platform(
                    session,
                    platform,
                    url
                )
            )

        results = await asyncio.gather(*tasks)

    final_text = (
        f"🌐 Username Results For @{username}\n"
        f"━━━━━━━━━━━━━━━\n\n"
        + "\n".join(results)
    )

    await loading.edit_text(final_text)


def main():

    if not BOT_TOKEN:

        logger.error("BOT_TOKEN not found")

        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))

    logger.info("Bot started successfully")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
