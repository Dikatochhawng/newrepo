import os
import re
from platform import python_version as kontol
from telethon import events, Button
from telegram import __version__ as telever
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from EmikoRobot.events import register
from EmikoRobot import telethn as tbot


PHOTO = "https://telegra.ph/file/770c41ad0f7bb7c7ad821.jpg"

@register(pattern=("/alive"))
async def awake(event):
  TEXT = f"**Chibai [{event.sender.first_name}](tg://user?id={event.sender.id}), kei hi Lynn ka ni.** \n\n"
  TEXT += "⚪ **Ka nungtha e** \n\n"
  TEXT += f"⚪ **Ka Bialpa : [Didiktea](https://t.me/Didiktea)** \n\n"
  TEXT += f"⚪ **Library Version :** `{telever}` \n\n"
  TEXT += f"⚪ **Telethon Version :** `{tlhver}` \n\n"
  TEXT += f"⚪ **Pyrogram Version :** `{pyrover}` \n\n"
  TEXT += "**Group a min Add avang hian ka lawm e ❤️**"
  BUTTON = [[Button.url("Help", "https://t.me/EmiexRobot?start=help"), Button.url("Support", "https://t.me/lynnsupportgroup")]]
  await tbot.send_file(event.chat_id, PHOTO, caption=TEXT,  buttons=BUTTON)
