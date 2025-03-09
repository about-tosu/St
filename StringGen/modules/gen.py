import asyncio
from pyrogram import Client, filters
from pyrogram.errors import (
    ApiIdInvalid,
    FloodWait,
    PasswordHashInvalid,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import (
    ApiIdInvalidError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from pyromod.listen.listen import ListenerTimeout
from config import SUPPORT_CHAT
from StringGen import Anony
from StringGen.utils import retry_key

async def gen_session(message, user_id: int, telethon: bool = False):
    ty = "ᴛᴇʟᴇᴛʜᴏɴ" if telethon else "ᴩʏʀᴏɢʀᴀᴍ v2"

    await message.reply_text(f"» ᴛʀʏɪɴɢ ᴛᴏ sᴛᴀʀᴛ {ty} sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴏʀ...")

    try:
        api_id = await Anony.ask(
            identifier=(message.chat.id, user_id, None),
            text="» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴀᴘɪ ɪᴅ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ:",
            filters=filters.text,
            timeout=300,
        )
    except ListenerTimeout:
        return await Anony.send_message(
            user_id, "» ᴛɪᴍᴇ ᴏᴜᴛ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.", reply_markup=retry_key
        )

    if not api_id.text.isdigit():
        return await Anony.send_message(user_id, "» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ᴀᴘɪ ɪᴅ.", reply_markup=retry_key)

    api_id = int(api_id.text)

    try:
        api_hash = await Anony.ask(
            identifier=(message.chat.id, user_id, None),
            text="» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴀᴘɪ ʜᴀsʜ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ:",
            filters=filters.text,
            timeout=300,
        )
    except ListenerTimeout:
        return await Anony.send_message(user_id, "» ᴛɪᴍᴇ ᴏᴜᴛ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.", reply_markup=retry_key)

    api_hash = api_hash.text.strip()
    if len(api_hash) < 30:
        return await Anony.send_message(user_id, "» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ᴀᴘɪ ʜᴀsʜ.", reply_markup=retry_key)

    try:
        phone_number = await Anony.ask(
            identifier=(message.chat.id, user_id, None),
            text="» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ:",
            filters=filters.text,
            timeout=300,
        )
    except ListenerTimeout:
        return await Anony.send_message(user_id, "» ᴛɪᴍᴇ ᴏᴜᴛ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.", reply_markup=retry_key)

    phone_number = phone_number.text.strip()

    await Anony.send_message(user_id, "» ᴛʀʏɪɴɢ ᴛᴏ sᴇɴᴅ ᴏᴛᴘ...")

    client = (
        TelegramClient(StringSession(), api_id, api_hash)
        if telethon
        else Client(name="Anony", api_id=api_id, api_hash=api_hash, in_memory=True)
    )

    await client.connect()

    try:
        code = await client.send_code_request(phone_number) if telethon else await client.send_code(phone_number)
    except (FloodWait, ApiIdInvalid, ApiIdInvalidError):
        return await Anony.send_message(user_id, "» ɪɴᴠᴀʟɪᴅ ᴄʀᴇᴅᴇɴᴛɪᴀʟs. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀᴘɪ ɪᴅ ᴀɴᴅ ᴀᴘɪ ʜᴀsʜ.", reply_markup=retry_key)
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        return await Anony.send_message(user_id, "» ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪs ɪɴᴠᴀʟɪᴅ.", reply_markup=retry_key)

    try:
        otp = await Anony.ask(
            identifier=(message.chat.id, user_id, None),
            text="» ᴇɴᴛᴇʀ ᴛʜᴇ ᴏᴛᴘ ʏᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ:",
            filters=filters.text,
            timeout=600,
        )
    except ListenerTimeout:
        return await Anony.send_message(user_id, "» ᴛɪᴍᴇ ᴏᴜᴛ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.", reply_markup=retry_key)

    otp = otp.text.replace(" ", "")
    try:
        if telethon:
            await client.sign_in(phone_number, otp)
        else:
            await client.sign_in(phone_number, code.phone_code_hash, otp)
    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        return await Anony.send_message(user_id, "» ᴏᴛᴘ ɪs ɪɴᴠᴀʟɪᴅ.", reply_markup=retry_key)
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        return await Anony.send_message(user_id, "» ᴏᴛᴘ ʜᴀs ᴇxᴘɪʀᴇᴅ.", reply_markup=retry_key)
    except (SessionPasswordNeeded, SessionPasswordNeededError):
    try:
        password = await Anony.ask(
            identifier=(message.chat.id, user_id, None),
            text="» 2-ꜱᴛᴇᴘ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴇɴᴀʙʟᴇᴅ. ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴘᴀssᴡᴏʀᴅ:",
            filters=filters.text,
            timeout=300,
        )
        password = password.text.strip()
        await client.check_password(password)
    except PasswordHashInvalid:
        return await Anony.send_message(user_id, "» ɪɴᴄᴏʀʀᴇᴄᴛ ᴘᴀssᴡᴏʀᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.", reply_markup=retry_key)
