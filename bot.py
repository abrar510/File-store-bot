from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from pyrogram.errors import UserNotParticipant

from database import (
    save_file,
    get_file,
    save_batch,
    get_batch
)

import os
import uuid
import asyncio

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
# BOT
# ==========================

app = Client(
    "FileStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==========================
# MEMORY
# ==========================

ACTIVE_BATCH = {}

# ==========================
# FORCE SUB CHECK
# ==========================

async def is_joined(user_id):

    try:

        member = await app.get_chat_member(
            FORCE_CHANNEL,
            user_id
        )

        return member.status not in [
            "left",
            "kicked"
        ]

    except UserNotParticipant:

        return False

    except Exception as e:

        print("JOIN ERROR:", e)

        return False

# ==========================
# JOIN BUTTON
# ==========================

def join_button(callback_data):

    return InlineKeyboardMarkup(
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
                    callback_data=callback_data
                )
            ]
        ]
    )

# ==========================
# AUTO DELETE
# ==========================

async def auto_delete(messages):

    await asyncio.sleep(
        AUTO_DELETE_TIME
    )

    for msg in messages:

        try:
            await msg.delete()
        except:
            pass
# ==========================
# SINGLE FILE STORE
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
async def single_file_store(
    client,
    message
):

    user_id = message.from_user.id

    # Batch Mode হলে Skip
    if user_id in ACTIVE_BATCH:
        return

    # Force Subscribe
    if not await is_joined(user_id):

        await message.reply_text(
            "⚠️ First Join Our Channel",
            reply_markup=join_button(
                "ignore"
            )
        )

        return

    try:

        stored = await message.copy(
            STORE_CHANNEL
        )

        file_code = str(
            uuid.uuid4()
        )[:8]

        await save_file(
            file_code,
            stored.id
        )

        me = await client.get_me()

        link = (
            f"https://t.me/"
            f"{me.username}"
            f"?start=file_{file_code}"
        )

        await message.reply_text(
            "✅ File Stored Successfully!\n\n"
            f"🔗 {link}"
        )

    except Exception as e:

        print(
            "STORE ERROR:",
            e
        )

        await message.reply_text(
            f"❌ Error:\n{e}"
        )


# ==========================
# CHECK FILE BUTTON
# ==========================

@app.on_callback_query(
    filters.regex("^checkfile_")
)
async def check_file_button(
    client,
    query: CallbackQuery
):

    file_code = query.data.replace(
        "checkfile_",
        ""
    )

    if not await is_joined(
        query.from_user.id
    ):

        await query.answer(
            "❌ Join Channel First",
            show_alert=True
        )

        return

    data = await get_file(
        file_code
    )

    if not data:

        await query.answer(
            "❌ File Not Found",
            show_alert=True
        )

        return

    sent = await client.copy_message(
        chat_id=query.message.chat.id,
        from_chat_id=STORE_CHANNEL,
        message_id=data["message_id"]
    )

    warn = await query.message.reply_text(
        "⚠️ File Will Be Deleted After 10 Minutes"
    )

    asyncio.create_task(
        auto_delete(
            [sent, warn]
        )
    )

    await query.answer(
        "✅ Verified",
        show_alert=True
    )
    # ==========================
# START BATCH
# ==========================

@app.on_message(filters.command("batch"))
async def start_batch(
    client,
    message
):

    ACTIVE_BATCH[
        message.from_user.id
    ] = []

    await message.reply_text(
        "📦 Batch Mode Started\n\n"
        "Send Files Now.\n"
        "When Finished Send /done"
    )


# ==========================
# BATCH COLLECTOR
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
async def batch_collector(
    client,
    message
):

    user_id = message.from_user.id

    if user_id not in ACTIVE_BATCH:
        return

    try:

        stored = await message.copy(
            STORE_CHANNEL
        )

        ACTIVE_BATCH[
            user_id
        ].append(
            stored.id
        )

        await message.reply_text(
            "✅ Added To Batch"
        )

    except Exception as e:

        print(
            "BATCH STORE ERROR:",
            e
        )

        await message.reply_text(
            "❌ Failed To Add File"
        )


# ==========================
# DONE BATCH
# ==========================

@app.on_message(filters.command("done"))
async def done_batch(
    client,
    message
):

    user_id = message.from_user.id

    if user_id not in ACTIVE_BATCH:

        await message.reply_text(
            "❌ No Active Batch"
        )

        return

    if len(
        ACTIVE_BATCH[user_id]
    ) == 0:

        await message.reply_text(
            "❌ No Files In Batch"
        )

        return

    try:

        batch_code = str(
            uuid.uuid4()
        )[:8]

        await save_batch(
            batch_code,
            ACTIVE_BATCH[user_id]
        )

        del ACTIVE_BATCH[
            user_id
        ]

        me = await client.get_me()

        link = (
            f"https://t.me/"
            f"{me.username}"
            f"?start=batch_{batch_code}"
        )

        await message.reply_text(
            "✅ Batch Created Successfully!\n\n"
            f"🔗 {link}"
        )

    except Exception as e:

        print(
            "DONE ERROR:",
            e
        )

        await message.reply_text(
            "❌ Failed To Create Batch"
        )
        # ==========================
# START HANDLER
# ==========================

@app.on_message(filters.command("start"))
async def start_handler(
    client,
    message
):

    if len(message.command) == 1:

        await message.reply_text(
            "📂 Send File For Single Link\n\n"
            "📦 Use /batch For Batch Link"
        )

        return

    param = message.command[1]

    # ======================
    # SINGLE FILE
    # ======================

    if param.startswith("file_"):

        file_code = param.replace(
            "file_",
            ""
        )

        if not await is_joined(
            message.from_user.id
        ):

            await message.reply_text(
                "⚠️ First Join Our Channel",
                reply_markup=join_button(
                    f"checkfile_{file_code}"
                )
            )

            return

        data = await get_file(
            file_code
        )

        if not data:

            await message.reply_text(
                "❌ File Not Found"
            )

            return

        sent = await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=STORE_CHANNEL,
            message_id=data["message_id"]
        )

        warn = await message.reply_text(
            "⚠️ File Will Be Deleted After 10 Minutes"
        )

        asyncio.create_task(
            auto_delete(
                [sent, warn]
            )
        )

        return

    # ======================
    # BATCH FILE
    # ======================

    if param.startswith("batch_"):

        batch_code = param.replace(
            "batch_",
            ""
        )

        if not await is_joined(
            message.from_user.id
        ):

            await message.reply_text(
                "⚠️ First Join Our Channel",
                reply_markup=join_button(
                    f"checkbatch_{batch_code}"
                )
            )

            return

        data = await get_batch(
            batch_code
        )

        if not data:

            await message.reply_text(
                "❌ Batch Not Found"
            )

            return

        sent_messages = []

        for msg_id in data["message_ids"]:

            sent = await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=STORE_CHANNEL,
                message_id=msg_id
            )

            sent_messages.append(
                sent
            )

        warn = await message.reply_text(
            "⚠️ Files Will Be Deleted After 10 Minutes"
        )

        sent_messages.append(
            warn
        )

        asyncio.create_task(
            auto_delete(
                sent_messages
            )
        )

        return


# ==========================
# CHECK BATCH BUTTON
# ==========================

@app.on_callback_query(
    filters.regex("^checkbatch_")
)
async def check_batch_button(
    client,
    query: CallbackQuery
):

    batch_code = query.data.replace(
        "checkbatch_",
        ""
    )

    if not await is_joined(
        query.from_user.id
    ):

        await query.answer(
            "❌ Join Channel First",
            show_alert=True
        )

        return

    data = await get_batch(
        batch_code
    )

    if not data:

        await query.answer(
            "❌ Batch Not Found",
            show_alert=True
        )

        return

    sent_messages = []

    try:

        for msg_id in data["message_ids"]:

            sent = await client.copy_message(
                chat_id=query.message.chat.id,
                from_chat_id=STORE_CHANNEL,
                message_id=msg_id
            )

            sent_messages.append(
                sent
            )

        warn = await query.message.reply_text(
            "⚠️ Files Will Be Deleted After 10 Minutes"
        )

        sent_messages.append(
            warn
        )

        asyncio.create_task(
            auto_delete(
                sent_messages
            )
        )

        await query.answer(
            "✅ Channel Verified",
            show_alert=True
        )

    except Exception as e:

        print(
            "BATCH ERROR:",
            e
        )

        await query.answer(
            "❌ Failed To Send Files",
            show_alert=True
        )


# ==========================
# IGNORE BUTTON
# ==========================

@app.on_callback_query(
    filters.regex("^ignore$")
)
async def ignore_button(
    client,
    query
):

    await query.answer(
        "Join Channel First",
        show_alert=True
    )


# ==========================
# RUN
# ==========================

print(
    "Bot Started Successfully"
)

app.run()
