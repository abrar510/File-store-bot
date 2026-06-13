import os
import asyncio
import secrets
from pymongo import MongoClient

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
OWNER_ID = int(os.getenv("OWNER_ID"))

CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
BOT_USERNAME = os.getenv("BOT_USERNAME")

mongo = MongoClient(MONGO_URI)
db = mongo["FileStoreBot"]
files = db["files"]


async def check_join(bot, user_id):
    try:
        member = await bot.get_chat_member(
            CHANNEL_USERNAME,
            user_id
        )

        return member.status not in ["left", "kicked"]

    except:
        return False


async def auto_delete(bot, chat_id, message_id):
    await asyncio.sleep(600)

    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except:
        pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if context.args:

        token = context.args[0]

        data = files.find_one(
            {"token": token}
        )

        if not data:
            await update.message.reply_text(
                "❌ Invalid Link"
            )
            return

        joined = await check_join(
            context.bot,
            user.id
        )

        if not joined:
            await update.message.reply_text(
                f"⚠️ প্রথমে {CHANNEL_USERNAME} চ্যানেলে Join করুন।"
            )
            return

        sent = await context.bot.send_document(
            chat_id=user.id,
            document=data["file_id"],
            caption="📁 File Ready"
        )

        context.application.create_task(
            auto_delete(
                context.bot,
                sent.chat_id,
                sent.message_id
            )
        )

        return

    await update.message.reply_text(
        "✅ File Store Bot Online"
    )


async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if not update.message.document:
        await update.message.reply_text(
            "শুধু Document আপলোড করুন।"
        )
        return

    file_id = update.message.document.file_id

    token = secrets.token_urlsafe(8)

    files.insert_one({
        "token": token,
        "file_id": file_id
    })

    link = (
        f"https://t.me/"
        f"{BOT_USERNAME}"
        f"?start={token}"
    )

    await update.message.reply_text(
        f"✅ Link Generated\n\n{link}"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    total = files.count_documents({})

    await update.message.reply_text(
        f"📦 Total Files: {total}"
    )


def main():

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("stats", stats)
    )

    app.add_handler(
        MessageHandler(
            filters.Document.ALL,
            upload
        )
    )

    print("Bot Started")

    app.run_polling()


if __name__ == "__main__":
    main()
