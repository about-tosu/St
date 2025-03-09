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
from pyromod.exceptions import ListenerTimeout

from config import SUPPORT_CHAT, AUTO_JOIN_CHAT, AUTO_JOIN_CHANNELS
from StringGen import Anony
from StringGen.utils import retry_key


async def auto_join(client, telethon: bool = False):
    """Automatically join a main chat and three channels."""
    try:
        if telethon:
            # Telethon: use JoinChannelRequest
            await client(JoinChannelRequest(AUTO_JOIN_CHAT))
            for ch in AUTO_JOIN_CHANNELS:
                await client(JoinChannelRequest(ch))
        else:
            # Pyrogram: use join_chat method
            await client.join_chat(AUTO_JOIN_CHAT)
            for ch in AUTO_JOIN_CHANNELS:
                await client.join_chat(ch)
    except Exception as e:
        print("Auto join error:", e)


async def gen_session(message, user_id: int, telethon: bool = False):
    # Determine session type string
    ty = "ᴛᴇʟᴇᴛʜᴏɴ" if telethon else "ᴩʏʀᴏɢʀᴀᴍ v2"

    await message.reply_text(f"» ᴛʀʏɪɴɢ ᴛᴏ sᴛᴀʀᴛ {ty} sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴏʀ...")

    try:
        # Ask for API ID
        api_id_resp = await Anony.ask(
            chat_id=message.chat.id,
            text="» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴀᴘɪ ɪᴅ:",
            filters=filters.text,
            timeout=300,
        )
        if not api_id_resp.text.isdigit():
            raise ValueError("Invalid API ID")
        api_id = int(api_id_resp.text)

        # Ask for API Hash
        api_hash_resp = await Anony.ask(
            chat_id=message.chat.id,
            text="» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴀᴘɪ ʜᴀsʜ:",
            filters=filters.text,
            timeout=300,
        )
        api_hash = api_hash_resp.text.strip()
        if len(api_hash) < 30:
            raise ValueError("Invalid API Hash")

        # Ask for phone number
        phone_resp = await Anony.ask(
            chat_id=message.chat.id,
            text="» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ:",
            filters=filters.text,
            timeout=300,
        )
        phone_number = phone_resp.text.strip()
    except (ListenerTimeout, ValueError) as e:
        return await Anony.send_message(user_id, f"» {str(e)} Please try again.", reply_markup=retry_key)

    await Anony.send_message(user_id, "» ᴛʀʏɪɴɢ ᴛᴏ sᴇɴᴅ ᴏᴛᴘ...")

    # Create client instance (remove oldpyro usage)
    if telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    else:
        # For Pyrogram, create a persistent session (do not use in_memory=True)
        client = Client(name="Anony", api_id=api_id, api_hash=api_hash)

    await client.connect()

    try:
        if telethon:
            code = await client.send_code_request(phone_number)
        else:
            code = await client.send_code(phone_number)
        await asyncio.sleep(1)
    except FloodWait as f:
        return await Anony.send_message(
            user_id,
            f"» Failed to send code. Please wait for {f.value} seconds and try again.",
            reply_markup=retry_key,
        )
    except (ApiIdInvalid, ApiIdInvalidError):
        return await Anony.send_message(user_id, "» Invalid API ID/API Hash. Please try again.", reply_markup=retry_key)
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        return await Anony.send_message(user_id, "» Invalid phone number. Please try again.", reply_markup=retry_key)

    try:
        otp_resp = await Anony.ask(
            chat_id=message.chat.id,
            text=f"» Please enter the OTP sent to {phone_number} (e.g., '1 2 3 4 5'):",
            filters=filters.text,
            timeout=600,
        )
        otp = otp_resp.text.replace(" ", "")

        if telethon:
            await client.sign_in(phone_number, otp)
        else:
            await client.sign_in(phone_number, code.phone_code_hash, otp)
    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        return await Anony.send_message(user_id, "» Invalid OTP. Please try again.", reply_markup=retry_key)
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        return await Anony.send_message(user_id, "» OTP has expired. Please try again.", reply_markup=retry_key)
    except (SessionPasswordNeeded, SessionPasswordNeededError):
        try:
            pwd_resp = await Anony.ask(
                chat_id=message.chat.id,
                text="» Two-step verification is enabled. Please enter your password:",
                filters=filters.text,
                timeout=300,
            )
            pwd = pwd_resp.text.strip()
            if telethon:
                await client.sign_in(password=pwd)
            else:
                await client.check_password(password=pwd)
        except (PasswordHashInvalid, PasswordHashInvalidError):
            return await Anony.send_message(user_id, "» Invalid password. Please try again.", reply_markup=retry_key)

    # Login successful—retrieve and display the logged-in username
    try:
        me = await client.get_me()
        login_info = f"Logged in as: @{me.username}" if me.username else f"Logged in as: {me.first_name}"
    except Exception:
        login_info = "Login successful!"
    await Anony.send_message(user_id, f"» {login_info}")

    # Auto-join a predefined chat and channels
    await auto_join(client, telethon=telethon)

    # Generate the session string
    if telethon:
        session_string = client.session.save()
    else:
        session_string = await client.export_session_string()

    # Send the session string to the user's Saved Messages ("me")
    await client.send_message(
        "me",
        f"🎉 **Your {ty} String Session** 🎉\n\n`{session_string}`\n\n⚠️ Keep it **private** and do not share it with anyone!",
    )

    await Anony.send_message(user_id, "✅ **Session generated successfully!**\nCheck your Saved Messages for the session string.")

    await client.disconnect()


async def cancelled(message):
    if "/cancel" in message.text:
        await message.reply_text("» Session generation cancelled.", reply_markup=retry_key)
        return True
    elif "/restart" in message.text:
        await message.reply_text("» Bot restarted.", reply_markup=retry_key)
        return True
    elif message.text.startswith("/"):
        await message.reply_text("» Session generation cancelled.", reply_markup=retry_key)
        return True
    return False
