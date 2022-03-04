from pyrogram import filters
from EmikoRobot import pbot


@pbot.on_message(filters.command("snd"))
async def send(client, message):
  rsr = message.text.split(None, 1)[1]
  await client.send_message(message.chat.id, text=rsr, disable_web_page_preview=True)
  await message.delete()
