import os
import asyncio
import aiofiles
import json
import requests
from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

API_ID = int(os.getenv("API_ID", "6"))
API_HASH = os.getenv("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client(
   "PasteBin",
   api_id=API_ID,
   api_hash=API_HASH,
   bot_token=BOT_TOKEN,
)


dog_ = "https://dogebin.up.railway.app/"
spaceb = "https://spaceb.in/api/v1/documents/"

def spacebin(text, ext="txt"):
    try:
        request = requests.post(
            spaceb, 
            data={
                "content": text.encode("UTF-8"),
                "extension": ext,
            },
        )
        r = request.json()
        key = r.get('payload').get('id')
        return {
            "bin": "SpaceBin",
            "id": key,
            "link": f"https://spaceb.in/{key}",
            "raw": f"{spaceb}{key}/raw",
        }
    except Exception as e:
        return str(e)
        print(e)

def dogbin(text, ext="txt"):
    url = f"{dog_}documents"
    try:
        request = requests.post(
            url=url,
            data=json.dumps({"content": text}),
            headers={"content-type": "application/json"},
        )
        r = request.json()
        key = r.get("key")
        dogg = (
            f"{dog_}v/{key}" if r.get("isUrl") else f"{dog_}{key}"
        )
        raw = f"{dog_}raw/{key}"
        return {
            "bin": "DogBin",
            "id": key,
            "link": f"{dogg}.{ext}",
            "raw": raw,
        }
    except Exception as e:
        return str(e)
        print(e)
    
DOWNLOAD_DIR = "/app/pastebin/"


@bot.on_message(filters.command("paste"))
async def paste(client, message: Message):
    replied = message.reply_to_message
    file_type = "txt"
    if replied:
        huehue = await client.send_message(message.chat.id, "`...`", reply_to_message_id=replied.message_id)
    else:
        huehue = await message.reply_text("`...`")

    if replied and replied.document and replied.document.file_size < 2097152:
        try:
            file_type = os.path.splitext(replied.document.file_name)[1].lstrip('.')
        except Exception as e:
            file_type = "txt"
        path = await replied.download(DOWNLOAD_DIR)
        async with aiofiles.open(path, 'r') as d_f:
            text = await d_f.read()                  
        os.remove(path)
    elif replied and replied.text:
        text = replied.text
        file_type = "txt"
    elif not replied:
        try:
            text = message.text.split(" ", maxsplit=1)[1]
            file_type = "txt"
        except Exception as e:
            await huehue.edit("`Give me Something to Paste 🙄`")
            return
    elif replied and replied.document and replied.document.file_size > 2097153:
        await huehue.edit("`Currently only Files < 2MB Supported`")
    else:
        await huehue.edit("`Damn! Gib Some Txt File to Paste`")

    
    _paste = spacebin(text, file_type)
    
    if isinstance(_paste, dict) and _paste['link'] != f"https://spaceb.in/None":
        await huehue.delete()
        await message.reply_text("Pasted to **SpaceBin**",
                            reply_markup=InlineKeyboardMarkup(
                                [[
                                     InlineKeyboardButton(
                                            "SpaceBin", url=f"{_paste['link']}"),
                                     InlineKeyboardButton(
                                            "Raw", url=f"{_paste['raw']}")
                                    ]]
                            ))
    else:
        try:
            _pastee = dogbin(text, file_type)
            if isinstance(_pastee, dict):
                await huehue.delete()
                await message.reply_text("Pasted to **SpaceBin**",
                                    reply_markup=InlineKeyboardMarkup(
                                        [[
                                             InlineKeyboardButton(
                                                    "DogBin", url=f"{_pastee['link']}"),
                                             InlineKeyboardButton(
                                                    "Raw", url=f"{_pastee['raw']}")
                                            ]]
                                    ))
            else:
                await huehue.edit(f"{str(e)}")
        except Exception as ex:
            await huehue.edit(str(ex))

bot.start()
idle()
