from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
import asyncio

# =========================
# CONFIG
# =========================

API_ID = 36675180
API_HASH = "c1a9924f9bb7ab9e31d76274bf82b571"
BOT_TOKEN = "8774111930:AAHbJM9RGVk_tuxkrMRI_iXMUwmUGYB9bK0"

# Force Subscribe Channel
FORCE_CHANNEL = -1003310527316

# Store Channel
STORE_CHANNEL = -1003603082549

# Auto Delete Time (Seconds)
AUTO_DELETE_TIME = 600

# Private Channel Link
CHANNEL_LINK = "https://t.me/+-zeuklTsZrgxODM1"

# =========================

app = Client(
    "FileStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# FORCE SUB CHECK
# =========================

async def is_joined(user_id):
    try:
        member = await app.get_chat_member(
            FORCE_CHANNEL,
            user_id
        )

        return member.status not in ["left", "kicked"]

    except:
        return False


# =========================
# AUTO DELETE
# =========================

async def delete_after(file_msg, warning_msg):
    await asyncio.sleep(AUTO_DELETE_TIME)

    try:
        await file_msg.delete()
    except:
        pass

    try:
        await warning_msg.delete()
    except:
        pass


# =========================
# START
# =========================

@app.on_message(filters.command("start"))
async def start_handler(client, message):

    user_id = message.from_user.id

    if not await is_joined(user_id):

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📢 Join Channel",
                        url=CHANNEL_LINK
                    )
                ]
            ]
        )

        await message.reply_text(
            "⚠️ আগে চ্যানেলে Join করুন।",
            reply_markup=buttons
        )
        return

    # Link open
    if len(message.command) > 1:

        try:
            file_id = int(message.command[1])

            sent = await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=STORE_CHANNEL,
                message_id=file_id
            )

            warn = await message.reply_text(
                "⚠️ এই ফাইল ১০ মিনিট পরে ডিলিট হবে।\n"
                "Saved Messages-এ ফরওয়ার্ড করে রাখুন।"
            )

            asyncio.create_task(
                delete_after(sent, warn)
            )

        except Exception:
            await message.reply_text(
                "❌ File Not Found."
            )

    else:

        await message.reply_text(
            "📂 আমাকে একটি File পাঠান।\n\n"
            "আমি Link তৈরি করে দেব।"
        )


# =========================
# STORE FILE
# =========================

@app.on_message(
    filters.private &
    (
        filters.document |
        filters.video |
        filters.audio |
        filters.photo
    )
)
async def store_file(client, message):

    user_id = message.from_user.id

    if not await is_joined(user_id):

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📢 Join Channel",
                        url=CHANNEL_LINK
                    )
                ]
            ]
        )

        await message.reply_text(
            "⚠️ আগে চ্যানেলে Join করুন।",
            reply_markup=buttons
        )
        return

    stored = await message.copy(
        STORE_CHANNEL
    )

    bot_username = (
        await client.get_me()
    ).username

    link = (
        f"https://t.me/"
        f"{bot_username}"
        f"?start={stored.id}"
    )

    await message.reply_text(
        f"✅ File Stored Successfully!\n\n"
        f"🔗 {link}"
    )


# =========================
# RUN
# =========================

print("Bot Started...")

app.run()
