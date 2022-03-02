import html
from EmikoRobot.modules.disable import DisableAbleCommandHandler
from EmikoRobot import dispatcher, DRAGONS
from EmikoRobot.modules.helper_funcs.extraction import extract_user
from telegram.ext import CallbackContext, CallbackQueryHandler
import EmikoRobot.modules.sql.approve_sql as sql
from EmikoRobot.modules.helper_funcs.chat_status import user_admin
from EmikoRobot.modules.log_channel import loggable
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.utils.helpers import mention_html
from telegram.error import BadRequest


@loggable
@user_admin
def approve(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I sawi awmzia ka hrethiam lo, chiang takin sawi rawh!",
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status in ("administrator", "creator"):
        message.reply_text(
            "User hi admin ani sa tawh a - locks, blocklists, leh antiflood te hi a chung ah apply ani lo.",
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"[{member.user['first_name']}](tg://user?id={member.user['id']}) hi {chat_title} ah approve ani e.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.approve(message.chat_id, user_id)
    message.reply_text(
        f"[{member.user['first_name']}](tg://user?id={member.user['id']}) hi {chat_title} ah approve ani e! Heng locks, blocklists, and antiflood te hian a chung ah awmzia a neilo ang.",
        parse_mode=ParseMode.MARKDOWN,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#APPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@loggable
@user_admin
def disapprove(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I sawi awmzia ka hrethiam lo, chiang takin sawi rawh!",
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status in ("administrator", "creator"):
        message.reply_text("He user hi admin ani a, unapprove theih a nilo.")
        return ""
    if not sql.is_approved(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} hi approve ala nilo!")
        return ""
    sql.disapprove(message.chat_id, user_id)
    message.reply_text(
        f"{member.user['first_name']} hi {chat_title} ah hian approve ani tawhlo.",
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNAPPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@user_admin
def approved(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "Heng users te hi approve te chu anni.\n"
    approved_users = sql.list_approved(message.chat_id)
    for i in approved_users:
        member = chat.get_member(int(i.user_id))
        msg += f"- `{i.user_id}`: {member.user['first_name']}\n"
    if msg.endswith("approved.\n"):
        message.reply_text(f"members tumah {chat_title} ah hian approve an nilo.")
        return ""
    message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@user_admin
def approval(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    member = chat.get_member(int(user_id))
    if not user_id:
        message.reply_text(
            "I sawi awmzia ka hrethiam lo, chiang takin sawi rawh!",
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"{member.user['first_name']} hi approve ani a. Locks, antiflood, and blocklists te hian awmzia a neilo.",
        )
    else:
        message.reply_text(
            f"{member.user['first_name']} hi approve ani lo. command hmang in an chung ah action lak theih ani.",
        )


def unapproveall(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        update.effective_message.reply_text(
            "Group siamtu chiah hian members te a rualin vawikhat ah a unapprove thei.",
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Unapprove all users",
                        callback_data="unapproveall_user",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Cancel",
                        callback_data="unapproveall_cancel",
                    ),
                ],
            ],
        )
        update.effective_message.reply_text(
            f"I chiang maw he Group {chat.title} a members te hi unapprove vek i duh maw? A sut theih tawhloh ania.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


def unapproveall_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "unapproveall_user":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            approved_users = sql.list_approved(chat.id)
            users = [int(i.user_id) for i in approved_users]
            for user_id in users:
                sql.disapprove(chat.id, user_id)
            message.edit_text("Successfully Unapproved all user in this Chat.")
            return

        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")

        if member.status == "member":
            query.answer("He thil ti tur hi chuan admin i nih angai.")
    elif query.data == "unapproveall_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            message.edit_text("approved user te remove na chu cancel ani.")
            return ""
        if member.status == "administrator":
            query.answer("He Group siamtu chauh hian he thil hi chu a ti thei.")
        if member.status == "member":
            query.answer("He thil ti tur hi chuan admin i nih angai.")


__help__ = """
Member nazawng ten Group an tihbuai loh nan he thil hi chu a tangkai.

Chuvang a approval hi siam ani.

*Admin Tan Chiah:*
❂ /approval*:* Approve leh approve loh en na (user message reply emaw command zawh ah username emaw ID dah tur).
❂ /approve*:* Member approve na (Approve hian Admin ang in hrem na tamtak an pumpelh thei).
❂ /unapprove*:* Approve tawh sa sut leh na.
❂ /approved*:* Approve tawh ho en na.
❂ /unapproveall*:* Approve tawh sa a rual a sut leh na..
"""

APPROVE = DisableAbleCommandHandler("approve", approve, run_async=True)
DISAPPROVE = DisableAbleCommandHandler("unapprove", disapprove, run_async=True)
APPROVED = DisableAbleCommandHandler("approved", approved, run_async=True)
APPROVAL = DisableAbleCommandHandler("approval", approval, run_async=True)
UNAPPROVEALL = DisableAbleCommandHandler("unapproveall", unapproveall, run_async=True)
UNAPPROVEALL_BTN = CallbackQueryHandler(
    unapproveall_btn, pattern=r"unapproveall_.*", run_async=True
)

dispatcher.add_handler(APPROVE)
dispatcher.add_handler(DISAPPROVE)
dispatcher.add_handler(APPROVED)
dispatcher.add_handler(APPROVAL)
dispatcher.add_handler(UNAPPROVEALL)
dispatcher.add_handler(UNAPPROVEALL_BTN)

__mod_name__ = "Approvals"
__command_list__ = ["approve", "unapprove", "approved", "approval"]
__handlers__ = [APPROVE, DISAPPROVE, APPROVED, APPROVAL]
