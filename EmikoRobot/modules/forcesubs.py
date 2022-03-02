import logging
import time

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

from EmikoRobot import DRAGONS as SUDO_USERS
from EmikoRobot import pbot
from EmikoRobot.modules.sql import forceSubscribe_sql as sql

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(
    lambda _, __, query: query.data == "onUnMuteRequest"
)


@pbot.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        channel = chat_db.channel
        chat_member = client.get_chat_member(chat_id, user_id)
        if chat_member.restricted_by:
            if chat_member.restricted_by.id == (client.get_me()).id:
                try:
                    client.get_chat_member(channel, user_id)
                    client.unban_chat_member(chat_id, user_id)
                    cb.message.delete()
                    # if cb.message.reply_to_message.from_user.id == user_id:
                    # cb.message.delete()
                except UserNotParticipant:
                    client.answer_callback_query(
                        cb.id,
                        text=f"❗ Kan @{channel} channel hi lo join la 'Unmute Me' tih kha i hmet dawn nia.",
                        show_alert=True,
                    )
            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ Admin ten an mute che chhan engemaw avangin.",
                    show_alert=True,
                )
        else:
            if (not client.get_chat_member(chat_id, (client.get_me()).id).status == "administrator"
            ):
                client.send_message(
                    chat_id,
                    f"❗ **{cb.from_user.mention} hi amahin in UnMute a tum a mahse ka unmute theilo admin ka ni silova.**\n__#Group chhuahsan mek...__",
                )

            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ Warning! button hmet kher suh type mai rawh.",
                    show_alert=True,
                )


@pbot.on_message(filters.text & ~filters.private & ~filters.edited, group=1)
def _check_member(client, message):
    chat_id = message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        user_id = message.from_user.id
        if (not client.get_chat_member(chat_id, user_id).status in ("administrator", "creator")
            and not user_id in SUDO_USERS
        ):
            channel = chat_db.channel
            try:
                client.get_chat_member(channel, user_id)
            except UserNotParticipant:
                try:
                    sent_message = message.reply_text(
                        "Chibai {} 🙏 \n **Kan @{} Channel hi lo join vela**👷 \n \nKhawngaihin [Kan Channel](https://t.me/{}) hi lo join la **UNMUTE ME** tih kha i hmet dawn nia. \n \n ".format(
                            message.from_user.mention, channel, channel
                        ),
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "Join Channel",
                                        url="https://t.me/{}".format(channel),
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        "Unmute Me", callback_data="onUnMuteRequest"
                                    )
                                ],
                            ]
                        ),
                    )
                    client.restrict_chat_member(
                        chat_id, user_id, ChatPermissions(can_send_messages=False)
                    )
                except ChatAdminRequired:
                    sent_message.edit(
                        "😕 **Lynn hi admin ani lova..**\n__Ban permissions min pe la lo try leh rawh.. \n#Ending FSub...__"
                    )

            except ChatAdminRequired:
                client.send_message(
                    chat_id,
                    text=f"😕 **Admin ka nilo a he @{channel} channel ah hian.**\n__Admin ah min dah la try leh rawh.\n#Ending FSub...__",
                )


@pbot.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == "creator" or user.user.id in SUDO_USERS:
        chat_id = message.chat.id
        if len(message.command) > 1:
            input_str = message.command[1]
            input_str = input_str.replace("@", "")
            if input_str.lower() in ("off", "no", "disable"):
                sql.disapprove(chat_id)
                message.reply_text("❌ **Force Subscribe tih thih ani e.**")
            elif input_str.lower() in ("clear"):
                sent_message = message.reply_text(
                    "**Member ka mute zawng zawngte ka unmute e...**"
                )
                try:
                    for chat_member in client.get_chat_members(
                        message.chat.id, filter="restricted"
                    ):
                        if chat_member.restricted_by.id == (client.get_me()).id:
                            client.unban_chat_member(chat_id, chat_member.user.id)
                            time.sleep(1)
                    sent_message.edit("✅ **Member ka mute zawng zawngte ka unmute e.**")
                except ChatAdminRequired:
                    sent_message.edit(
                        "😕 **Admin ka nilo a he Group ah hian.**\n__Admin ka nilo a he Group ah hian, admin ah min dahla i try leh dawn nia.__"
                    )
            else:
                try:
                    client.get_chat_member(input_str, "me")
                    sql.add_channel(chat_id, input_str)
                    message.reply_text(
                        f"✅ **Force Subscribe Tihnun ani e**\n__Force Subscribe tihnun ani a, members ten message thawn thei tur chuan he [channel](https://t.me/{input_str}) hi subscribe vek tur ani.__",
                        disable_web_page_preview=True,
                    )
                except UserNotParticipant:
                    message.reply_text(
                        f"😕 **Admin ka ni a**\n__Admin ka nilo a he [channel](https://t.me/{input_str}) ah hian. ForceSubscribe ti nung tur chuan admin ah min dah rawh.__",
                        disable_web_page_preview=True,
                    )
                except (UsernameNotOccupied, PeerIdInvalid):
                    message.reply_text(f"❗ **Channel Hming a diklo.**")
                except Exception as err:
                    message.reply_text(f"❗ **ERROR:** ```{err}```")
        else:
            if sql.fs_settings(chat_id):
                message.reply_text(
                    f"✅ **Force Subscribe is enabled in this chat.**\n__For this [Channel](https://t.me/{sql.fs_settings(chat_id).channel})__",
                    disable_web_page_preview=True,
                )
            else:
                message.reply_text("❌ **Force Subscribe tih thih ani e.**")
    else:
        message.reply_text(
            "❗ **Group Creator angai**\n__Hethil ti tur hi chuan Group creator i nih angai.__"
        )


__help__ = """
*Force Subscribe:*
❂ I Channel an subscribe hma chuan Lynn hian member te a mute thei
❂ I tihnun chuan member i channel subscribe lo te chu ka mute vek anga, an subscribe veleh ka unmute ang.
❂*Setup Dan*
*Creator tan bik*
❂ I Group ah min add in admin ah min dah rawh
❂ I channel ah min add in admin ah min dah rawh 
 
*Commmands*
❂ /fsub {channel hming} - Channel subscribe tur a tihna.
  💡Heihi ti hmasa rawh...
❂ /fsub - Setting hmanlai mek enna.
❂ /fsub disable - ForceSubscribe off na..
  💡Fsub hi i off chuan hna thawk leh turin i on leh angai.. /fsub {channel hming} 
❂ /fsub clear - Member mute lai mek te unmute na.
*Federation*
Federation hi hmunkhat aṭanga hmun hrang hrang ami tepawh hrem theih na'n a duan ania, a hmang ṭangkai thiam tan chuan ṭangkai tak ani..\n
*Commands:*\n
Command en na hran chi 3 a awm a, chu te chu.
• `/fedownerhelp`*:* Federation siamtu pual bik command en na.
• `/fedadminhelp`*:* Federation Admin pual bik command en na
• `/feduserhelp`*:* Tu tan pawh he command hi chu a hman theih, command awm te en na ani e.
"""
__mod_name__ = "F-Sub/Feds"
