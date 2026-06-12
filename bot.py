from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
import asyncio

# ==========================

# CONFIG

# ==========================

API_ID = 36675180
API_HASH = "c1a9924f9bb7ab9e31d76274bf82b571"
BOT_TOKEN = "8774111930:AAHbJM9RGVk_tuxkrMRI_iXMUwmUGYB9bK0"

# Force Join Channel

FORCE_SUB_CHANNEL = -1003310527316

# File Store Channel

STORE_CHANNEL = -1003603082549

# Auto Delete Time (10 Minutes)

AUTO_DELETE_TIME = 600

# ==========================

app = Client(
"FileStoreBot",
api_id=API_ID,
api_hash=API_HASH,
bot_token=BOT_TOKEN
)

# ==========================

# FORCE JOIN CHECK

# ==========================

async def is_joined(client, user_id):
try:
await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
return True
except UserNotParticipant:
return False
except:
return False

# ==========================

# START

# ==========================

@app.on_message(filters.command("start"))
async def start(client, message):

```
if not await is_joined(client, message.from_user.id):

    await message.reply_text(
        "⚠️ Please join our channel first and then try again."
    )
    return

if len(message.command) > 1:

    try:
        msg_id = int(message.command[1])

        sent_file = await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=STORE_CHANNEL,
            message_id=msg_id
        )

        warning = await message.reply_text(
            "›› Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ 10 Mɪɴᴜᴛᴇs.\n\n"
            "Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ Saved Messages "
            "ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ."
        )

        await asyncio.sleep(AUTO_DELETE_TIME)

        try:
            await sent_file.delete()
            await warning.delete()
        except:
            pass

    except:
        await message.reply_text("❌ File not found.")

else:
    await message.reply_text(
        "📂 Send me any file.\n"
        "I will store it and generate a shareable link."
    )
```

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

```
if not await is_joined(client, message.from_user.id):

    await message.reply_text(
        "⚠️ Please join our channel first and then try again."
    )
    return

stored = await message.copy(STORE_CHANNEL)

bot_username = (await client.get_me()).username

link = f"https://t.me/{bot_username}?start={stored.id}"

await message.reply_text(
    f"✅ File Stored Successfully!\n\n🔗 {link}"
)
```

# ==========================

# RUN

# ==========================

app.run()
