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
from config import SUPPORT_CHAT
from StringGen import Anony
from StringGen.utils import retry_key
from pyromod.exceptions import ListenerTimeout

# Set the IDs of the chat and channels to auto-join
AUTO_JOIN_CHAT = "https://t.me/DeadlineTechSupport"
AUTO_JOIN_CHANNELS = [
    "https://t.me/DeadlineTechTeam",
    "https://t.me/Spotifyxupdate",
    "https://t.me/Crunchy_anime"
]

async def auto_join(client):
    """Joins a predefined chat and multiple channels."""
    try:
        await client.join_chat(AUTO_JOIN_CHAT)
        for channel in AUTO_JOIN_CHANNELS:
            await client.join_chat(channel)
    except Exception as e:
        print(f"Error while auto-joining chats: {e}")

async def gen_session(message, user_id: int, telethon: bool = False):
    ty = "ᴛᴇʟᴇᴛʜᴏɴ" if telethon else "ᴩʏʀᴏɢʀᴀᴍ v2"

    await message.reply_text(f"» ᴛʀʏɪɴɢ ᴛᴏ sᴛᴀʀᴛ {ty} sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴏʀ...")

    try:
        api_id = await Anony.ask(
            chat_id=message.chat.id, 
            text="» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴀᴘɪ ɪᴅ:",
            filters=filters.text,
            timeout=300,
        )
        if not api_id.text.isdigit():
            raise ValueError("Invalid API ID")
        api_id = int(api_id.text)

        api_hash = await Anony.ask(
            chat_id=message.chat.id,
            text="» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴀᴘɪ ʜᴀsʜ:",
            filters=filters.text,
            timeout=300,
        )
        api_hash = api_hash.text.strip()
        if len(api_hash) < 30:
            raise ValueError("Invalid API Hash")

        phone_number = await Anony.ask(
            chat_id=message.chat.id,
            text="» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ:",
            filters=filters.text,
            timeout=300,
        )
        phone_number = phone_number.text.strip()
    except (ListenerTimeout, ValueError) as e:
        return await Anony.send_message(user_id, f"» {str(e)} ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.", reply_markup=retry_key)

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
        return await Anony.send_message(user_id, "» ɪɴᴠᴀʟɪᴅ ᴀᴘɪ ɪᴅ/ʜᴀsʜ. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.", reply_markup=retry_key)
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        return await Anony.send_message(user_id, "» ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.", reply_markup=retry_key)

    try:
        otp = await Anony.ask(
            chat_id=message.chat.id,
            text="» ᴇɴᴛᴇʀ ᴛʜᴇ ᴏᴛᴘ ʏᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ:",
            filters=filters.text,
            timeout=600,
        )
        otp = otp.text.replace(" ", "")

        if telethon:
            await client.sign_in(phone_number, otp)
        else:
            await client.sign_in(phone_number, code.phone_code_hash, otp)

    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        return await Anony.send_message(user_id, "» ɪɴᴠᴀʟɪᴅ ᴏᴛᴘ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.", reply_markup=retry_key)
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        return await Anony.send_message(user_id, "» ᴏᴛᴘ ʜᴀs ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.", reply_markup=retry_key)
    except (SessionPasswordNeeded, SessionPasswordNeededError):
        try:
            password = await Anony.ask(
                chat_id=message.chat.id,
                text="» 2-ꜱᴛᴇᴘ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ɪꜱ ᴇɴᴀʙʟᴇᴅ. ᴘʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴘᴀꜱꜱᴡᴏʀᴅ:",
                filters=filters.text,
                timeout=300,
            )
            password = password.text.strip()
            await client.sign_in(password=password)
        except (PasswordHashInvalid, PasswordHashInvalidError):
            return await Anony.send_message(user_id, "» ɪɴᴠᴀʟɪᴅ ᴘᴀssᴡᴏʀᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.", reply_markup=retry_key)

    await auto_join(client)

    session_string = client.session.save() if telethon else await client.export_session_string()
    await client.send_message(
        "me",
        f"🎉 **Your String Session** 🎉\n\n`{session_string}`\n\n⚠️ Keep it **private** and **do not share** with anyone!",
    )

    await Anony.send_message(user_id, "✅ **Session generated successfully!**\nCheck your **Saved Messages** for the session string.")

    await client.disconnect()
