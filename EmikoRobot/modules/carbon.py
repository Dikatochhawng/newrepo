from platform import python_version as y
from telegram import __version__ as o
from pyrogram import __version__ as z
from telethon import __version__ as s
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters
from EmikoRobot import pbot
from EmikoRobot.utils.errors import capture_err
from EmikoRobot.utils.functions import make_carbon


@pbot.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message):
    if not message.reply_to_message:
        return await message.reply_text("`Carbon siam tur chuanText message reply rawh.`")
    if not message.reply_to_message.text:
        return await message.reply_text("`Carbon siam tur chuanText message reply rawh.`")
    m = await message.reply_text("`Carbon Buatsaih mek ani`")
    carbon = await make_carbon(message.reply_to_message.text)
    await m.edit("`Uploading`")
    await pbot.send_photo(message.chat.id, carbon)
    await m.delete()
    carbon.close()


MEMEK = "https://telegra.ph/file/13bfc9bb06beb9bb38df6.jpg"

@pbot.on_message(filters.command("repo"))
async def repo(_, message):
    await message.reply_photo(
        photo=MEMEK,
        caption=f"""✨ **Chibai kei hi Lynn ka ni** 

**Owner repo : [Didiktea](https://t.me/Didiktea)**
**Python Version :** `{y()}`
**Library Version :** `{o}`
**Telethon Version :** `{s}`
**Pyrogram Version :** `{z}`

**Nangma Puala i neih ve duh chuan a hnuai a button khu hmet rawh.**
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Repo", url="https://github.com/Didiktea9/lynn"), 
                    InlineKeyboardButton(
                        "Support", url="https://t.me/lynnsupportgroup")
                ]
            ]
        )
    )
