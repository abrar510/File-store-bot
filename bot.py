
# ==========================
# CONFIG
# ==========================
API_ID = "36675180"
API_HASH = "c1a9924f9bb7ab9e31d76274bf82b571"
BOT_TOKEN = "8774111930:AAHbJM9RGVk_tuxkrMRI_iXMUwmUGYB9bK0"

# Example: -1001234567890
CHANNEL_ID = -1001234567890

AUTO_DELETE_TIME = 300  # 5 minutes
# ==========================

app = Client(
    "FileStoreBot",
    api_id= 36675180,
    api_hash=c1a9924f9bb7ab9e31d76274bf82b571,
    bot_token= 8774111930:AAHbJM9RGVk_tuxkrMRI_iXMUwmUGYB9bK0
)

# ==========================
# START COMMAND
# ==========================
@app.on_message(filters.command("start"))
async def start_handler(client, message):

    if len(message.command) > 1:

        try:
            file_msg_id = int(message.command[1])

            sent_file = await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id= -1003603082549,
                message_id=file_msg_id
            )

            notice = await message.reply_text(
                f"⚠️ This file will be deleted automatically in {AUTO_DELETE_TIME//60} minutes."
            )

            await asyncio.sleep(AUTO_DELETE_TIME)

            try:
                await sent_file.delete()
                await notice.delete()
            except:
                pass

        except Exception:
            await message.reply_text("❌ File not found.")

    else:
        await message.reply_text(
            "📂 Send me any file.\n"
            "I will store it and generate a shareable link."
        )

# ==========================
# STORE FILES
# ==========================
@app.on_message(
    filters.private &
    (filters.document |
     filters.video |
     filters.audio |
     filters.photo)
)
async def store_file(client, message):

    stored = await message.copy(-1003603082549)

    bot_username = (await client.get_me()).username

    link = f"https://t.me/akfilestorev1bot?start={stored.id}"

    await message.reply_text(
        f"✅ File Stored Successfully!\n\n"
        f"🔗 Share Link:\n{link}"
    )

# ==========================
# RUN BOT
# ==========================
app.run()
