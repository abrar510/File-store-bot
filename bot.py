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

import os

API_ID = int(os.getenv("API_ID"))

API_HASH = os.getenv("API_HASH")

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Force Subscribe Channel
FORCE_CHANNEL = int(os.getenv("FORCE_CHANNEL"))

# Store Channel
STORE_CHANNEL = int(os.getenv("STORE_CHANNEL"))

# Auto Delete Time (Seconds)
AUTO_DELETE_TIME = 600

# Public Channel Link
CHANNEL_LINK = os.getenv("CHANNEL_LINK")
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
                callback_data="checksub"
            )
        ]
    ]
)

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
        ],
        [
            InlineKeyboardButton(
                "✅ Check Channel",
                callback_data="checksub"
            )
        ]
    ]
)

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
               "›› Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ 10 Mɪɴᴜᴛᴇs.\n\n"
    "Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ Saved Messages ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ."
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
            "📂 Send me a File\n\n"
            "I will give you a Link"
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
        ],
        [
            InlineKeyboardButton(
                "✅ Check Channel",
                callback_data="checksub"
            )
        ]
    ]
)

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
from pyrogram.types import CallbackQuery

@app.on_callback_query(filters.regex("checksub"))
async def check_sub_callback(client, query: CallbackQuery):

    user_id = query.from_user.id

    if await is_joined(user_id):

        await query.answer(
            "✅ Channel Verified!",
            show_alert=True
        )

        await query.message.edit_text(
            "✅ Channel Verified!\n\n"
            "এখন আবার Link Open করুন।"
        )

    else:

        await query.answer(
            "❌ এখনও Channel Join করেননি!",
            show_alert=True
        )
app.run()
