from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from pyrogram.errors import UserNotParticipant
import asyncio
import os

# ==========================
# CONFIG
# ==========================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

FORCE_CHANNEL = int(os.getenv("FORCE_CHANNEL"))
STORE_CHANNEL = int(os.getenv("STORE_CHANNEL"))
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

AUTO_DELETE_TIME = 600

# ==========================

app = Client(
    "FileStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==========================
# JOIN CHECK
# ==========================

async def is_joined(user_id):
    try:
        await app.get_chat_member(
            FORCE_CHANNEL,
            user_id
        )
        return True

    except UserNotParticipant:
        return False

    except Exception as e:
        print("JOIN CHECK ERROR:", e)
        return False

# ==========================
# AUTO DELETE
# ==========================

async def auto_delete(file_msg, text_msg):
    await asyncio.sleep(AUTO_DELETE_TIME)

    try:
        await file_msg.delete()
    except:
        pass

    try:
        await text_msg.delete()
    except:
        pass

# ==========================
# START
# ==========================

@app.on_message(filters.command("start"))
async def start_command(client, message):

    if len(message.command) <= 1:
        await message.reply_text(
            "📂 Send me a file.\nI will generate a share link."
        )
        return

    file_id = message.command[1]

    if not await is_joined(message.from_user.id):

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📢 Join Channel",
                        url=CHANNEL_LINK
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ Check Channel",
                        callback_data=f"check#{file_id}"
                    )
                ]
            ]
        )

        await message.reply_text(
            "⚠️ First join our channel.",
            reply_markup=buttons
        )
        return

    try:

        sent = await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=STORE_CHANNEL,
            message_id=int(file_id)
        )

        warn = await message.reply_text(
            "⚠️ This file will be deleted after 10 minutes."
        )

        asyncio.create_task(
            auto_delete(sent, warn)
        )

    except Exception as e:
        print(e)
        await message.reply_text(
            "❌ File Not Found."
        )

# ==========================
# CHECK CHANNEL
# ==========================

@app.on_callback_query(filters.regex("^check#"))
async def check_channel(client, query: CallbackQuery):

    user_id = query.from_user.id
    file_id = query.data.split("#")[1]

    if not await is_joined(user_id):

        await query.answer(
            "❌ You still haven't joined the channel.",
            show_alert=True
        )
        return

    try:

        sent = await client.copy_message(
            chat_id=query.message.chat.id,
            from_chat_id=STORE_CHANNEL,
            message_id=int(file_id)
        )

        warn = await query.message.reply_text(
            "⚠️ This file will be deleted after 10 minutes."
        )

        asyncio.create_task(
            auto_delete(sent, warn)
        )

        await query.answer(
            "✅ Channel Verified",
            show_alert=True
        )

    except Exception as e:
        print(e)

        await query.answer(
            "❌ File Not Found",
            show_alert=True
        )

# ==========================
# STORE FILE
# ==========================

@app.on_message(
    filters.private &
    (
        filters.document |
        filters.video |
        filters.audio |
        filters.photo |
        filters.animation
    )
)
async def store_file(client, message):

    stored = await message.copy(
        STORE_CHANNEL
    )

    bot_username = (
        await client.get_me()
    ).username

    link = (
        f"https://t.me/{bot_username}"
        f"?start={stored.id}"
    )

    await message.reply_text(
        f"✅ File Stored Successfully!\n\n🔗 {link}"
    )

# ==========================
# RUN
# ==========================

print("Bot Started...")

app.run()
