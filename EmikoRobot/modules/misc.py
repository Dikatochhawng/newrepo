import time
import os
import re
import codecs
from typing import List
from random import randint
from EmikoRobot.modules.helper_funcs.chat_status import user_admin
from EmikoRobot.modules.disable import DisableAbleCommandHandler
from EmikoRobot import (
    dispatcher,
    WALL_API,
)
import requests as r
import wikipedia
from requests import get, post
from telegram import (
    Chat,
    ChatAction,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Message,
    MessageEntity,
    TelegramError,
)
from telegram.error import BadRequest
from telegram.ext.dispatcher import run_async
from telegram.ext import CallbackContext, Filters, CommandHandler
from EmikoRobot import StartTime
from EmikoRobot.modules.helper_funcs.chat_status import sudo_plus
from EmikoRobot.modules.helper_funcs.alternate import send_action, typing_action

MARKDOWN_HELP = f"""
Markdown is a very powerful formatting tool supported by telegram. {dispatcher.bot.first_name} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.

❂ <code>_italic_</code>: 👈 He mi sign a i thu hual khung a piang kha italic text (hawrawp âwn) ah a chang ang.
❂ <code>*bold*</code>: 👈 He mi sign hmang a i thu hual khung a piang kha bold text (hawrawp lian) ah a chang ang
❂ <code>`code`</code>: 👈 He mi sign a i thu hual khung a piang kha monospace text (hawrawp inkar zau) ah a chang ang.
❂ <code>[sometext](someURL)</code>: 👈 He mi sign a i thu hual khung a piang kha link - ah a chang zel ang <code>sometext</code>, \
han ticchin mah teh <code>someURL</code>.
<b>Example:</b><code>[Didiktea](example.com)</code>

❂ <code>[buttontext](buttonurl:someURL)</code>: Button siamdan ania, Button hming tur tih aia i hming dah kha Button a thu awm tur ania,  \
buttonurl: tih zawh a i link dah kha button an hmeh veleh an lut thei ang \
(link ah khan https:// tih lai chin zawng kha paih zel tur).
<b>Example:</b> <code>[Didiktea](buttonurl:example.com)</code>

Button hi line khat ah pakhat aia tam a dah theih a, a tihdan chu

[Button 1](buttonurl://example.com)
[Button 1](buttonurl://google.com:same)

Tihian button hi a indawt a awm kher lo in line khat ah pakhat aia tam i dah thei ang!
"""


@user_admin
def echo(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    else:
        message.reply_text(
            args[1], quote=False, parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    message.delete()


def markdown_help_sender(update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see, and Use #test!"
    )
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, *bold*, code, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)"
    )


def markdown_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        update.effective_message.reply_text(
            "Contact me in pm",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Markdown help",
                            url=f"t.me/{context.bot.username}?start=markdownhelp",
                        )
                    ]
                ]
            ),
        )
        return
    markdown_help_sender(update)


def wiki(update: Update, context: CallbackContext):
    kueri = re.split(pattern="wiki", string=update.effective_message.text)
    wikipedia.set_lang("en")
    if len(str(kueri[1])) == 0:
        update.effective_message.reply_text("Enter keywords!")
    else:
        try:
            pertama = update.effective_message.reply_text("🔄 Loading...")
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔧 More Info...",
                            url=wikipedia.page(kueri).url,
                        )
                    ]
                ]
            )
            context.bot.editMessageText(
                chat_id=update.effective_chat.id,
                message_id=pertama.message_id,
                text=wikipedia.summary(kueri, sentences=10),
                reply_markup=keyboard,
            )
        except wikipedia.PageError as e:
            update.effective_message.reply_text(f"⚠ Error: {e}")
        except BadRequest as et:
            update.effective_message.reply_text(f"⚠ Error: {et}")
        except wikipedia.exceptions.DisambiguationError as eet:
            update.effective_message.reply_text(
                f"⚠ Error\n There are too many query! Express it more!\nPossible query result:\n{eet}"
            )


@send_action(ChatAction.UPLOAD_PHOTO)
def wall(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    msg = update.effective_message
    msg_id = update.effective_message.message_id
    args = context.args
    query = " ".join(args)
    if not query:
        msg.reply_text("Please enter a query!")
        return
    caption = query
    term = query.replace(" ", "%20")
    json_rep = r.get(
        f"https://wall.alphacoders.com/api2.0/get.php?auth={WALL_API}&method=search&term={term}"
    ).json()
    if not json_rep.get("success"):
        msg.reply_text("An error occurred!")

    else:
        wallpapers = json_rep.get("wallpapers")
        if not wallpapers:
            msg.reply_text("No results found! Refine your search.")
            return
        index = randint(0, len(wallpapers) - 1)  # Choose random index
        wallpaper = wallpapers[index]
        wallpaper = wallpaper.get("url_image")
        wallpaper = wallpaper.replace("\\", "")
        context.bot.send_photo(
            chat_id,
            photo=wallpaper,
            caption="Preview",
            reply_to_message_id=msg_id,
            timeout=60,
        )
        context.bot.send_document(
            chat_id,
            document=wallpaper,
            filename="wallpaper",
            caption=caption,
            reply_to_message_id=msg_id,
            timeout=60,
        )


__help__ = """
*Available commands:*

❂ /markdownhelp*:* Markdownhelp a hman theih command te
❂ /paste*:* kan thu type te link a siam na
❂ /react*:* React na 
❂ /ud <Thu>*:* Thu type rawh
❂ /reverse*:* Thlalak leh sticker zawnna.
❂ /wiki <query>*:* wikipedia a thil zawnna
❂ /wall <query>*:* Wallpaper zawnna
❂ /cash*:* currency Hriatna
 Entirna:
 `/cash 1 USD INR`  
      _OR_
 `/cash 1 usd inr`
 Output: `1.0 USD = 75.505 INR`
"""

ECHO_HANDLER = DisableAbleCommandHandler(
    "echo", echo, filters=Filters.chat_type.groups, run_async=True)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, run_async=True)
WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki)
WALLPAPER_HANDLER = DisableAbleCommandHandler("wall", wall, run_async=True)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(WIKI_HANDLER)
dispatcher.add_handler(WALLPAPER_HANDLER)

__mod_name__ = "Extras"
__command_list__ = ["id", "echo", "wiki", "wall"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
    WIKI_HANDLER,
    WALLPAPER_HANDLER,
]
