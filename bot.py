```python
from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
import asyncio
import os

# =========================
# CONFIG
# =========================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

FORCE_CHANNEL = int(os.getenv("FORCE_CHANNEL"))
STORE_CHANNEL = int(os.getenv("STORE_CHANNEL"))

CHANNEL_LINK = os.getenv("CHANNEL_LINK")

AUTO_DELETE_TIME = 600

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


# =========================
# AUTO DELETE
# =========================

async def auto_delete(file_msg, warn_msg):
    await asyncio.sleep(AUTO_DELETE_TIME)

    try:
        await file_msg.delete()
    except:
        pass

    try:
        await warn_msg.delete()
    except:
        pass


# =========================
# START
# =========================

@app.on_message(filters.command("start"))
async def start_handler(client, message):

    user_id = message.from_user.id

    # file link
    if len(message.command) > 1:

        file_id = message.command[1]

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
                            callback_data=f"check_{file_id}"
                        )
                    ]
                ]
            )

            await message.reply_text(
                "⚠️ First Join Our Channel.",
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
                "⚠️ File will be deleted after 10 minutes.\n"
                "Forward it to Saved Messages."
            )

            asyncio.create_task(
                auto_delete(sent, warn)
            )

        except Exception as e:
            print(e)

            await message.reply_text(
                "❌ File Not Found."
            )

    else:

        await message.reply_text(
            "📂 Send me a file.\n\n"
            "I will generate a share link."
        )


# =========================
# CHECK CHANNEL BUTTON
# =========================

@app.on_callback_query(filters.regex("^check_"))
async def check_channel(client, query: CallbackQuery):

    user_id = query.from_user.id

    file_id = query.data.split("_")[1]

    if await is_joined(user_id):

        try:

            sent = await client.copy_message(
                chat_id=query.message.chat.id,
                from_chat_id=STORE_CHANNEL,
                message_id=int(file_id)
            )

            warn = await query.message.reply_text(
                "⚠️ File will be deleted after 10 minutes.\n"
                "Forward it to Saved Messages."
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

    else:

        await query.answer(
            "❌ Join Channel First",
            show_alert=True
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
        filters.photo |
        filters.animation
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
            "⚠️ Join Our Channel First.",
            reply_markup=buttons
        )

        return

    try:

        stored = await message.copy(
            STORE_CHANNEL
        )

        me = await client.get_me()

        link = (
            f"https://t.me/"
            f"{me.username}"
            f"?start={stored.id}"
        )

        await message.reply_text(
            f"✅ File Stored Successfully!\n\n"
            f"🔗 {link}"
        )

    except Exception as e:

        print(e)

        await message.reply_text(
            "❌ Failed To Store File."
        )


# =========================
# RUN
# =========================

print("Bot Started...")

app.run()
```
