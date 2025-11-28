#(©)Codeflix_Bots

import logging
import base64
import random
import re
import string
import time
import asyncio

from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import (
    ADMINS,
    FORCE_MSG,
    START_MSG,
    CUSTOM_CAPTION,
    IS_VERIFY,
    VERIFY_EXPIRE,
    VERIFY_EXPIRE_1,
    VERIFY_EXPIRE_2,
    VERIFY_GAP_TIME,
    SHORTLINK_API,
    SHORTLINK_URL,
    SHORTLINK_API_1,
    SHORTLINK_URL_1,
    SHORTLINK_API_2,
    SHORTLINK_URL_2,
    DISABLE_CHANNEL_BUTTON,
    PROTECT_CONTENT,
    TUT_VID,
    OWNER_ID,
    VERIFY_IMAGE,
)
from helper_func import subscribed, encode, decode, get_messages, get_shortlink, get_verify_status, update_verify_status, get_exp_time, get_verify_image
from database.database import add_user, del_user, full_userbase, present_user, db_get_link
from shortzy import Shortzy


def is_dual_verification_enabled():
    """Check if dual verification system is fully configured"""
    return bool(SHORTLINK_URL_2 and SHORTLINK_API_2)


async def send_verification_message(message, caption_text, verify_image, reply_markup):
    """Send verification message with or without image"""
    if verify_image and isinstance(verify_image, str) and verify_image.strip():
        try:
            await message.reply_photo(
                photo=verify_image,
                caption=caption_text,
                reply_markup=reply_markup,
                protect_content=False,
                quote=True
            )
        except:
            # If image fails, send text only
            await message.reply(caption_text, reply_markup=reply_markup, protect_content=False, quote=True)
    else:
        await message.reply(caption_text, reply_markup=reply_markup, protect_content=False, quote=True)


@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    owner_id = ADMINS  # Fetch the owner's ID from config

    # Check if the user is the owner
    if id == owner_id:
        # Owner-specific actions
        # You can add any additional actions specific to the owner here
        await message.reply("You are the owner! Additional actions can be added here.")

    else:
        if not await present_user(id):
            try:
                await add_user(id)
            except:
                pass

        verify_status = await get_verify_status(id)
        
        if 'current_step' not in verify_status:
            verify_status['current_step'] = 0
        if 'verify1_expiry' not in verify_status:
            verify_status['verify1_expiry'] = 0
        if 'verify2_expiry' not in verify_status:
            verify_status['verify2_expiry'] = 0
        if 'gap_expiry' not in verify_status:
            verify_status['gap_expiry'] = 0

        now = time.time()
        
        if "verify_" in message.text:
            _, token = message.text.split("_", 1)
            if verify_status['verify_token'] != token:
                return await message.reply("Your token is invalid or Expired. Try again by clicking /start")
            
            step = verify_status['current_step']
            
            # STEP 1 verification
            if step == 0 and token == verify_status['verify_token']:
                verify_status['current_step'] = 1
                verify_status['is_verified'] = True
                verify_status['verify1_expiry'] = now + VERIFY_EXPIRE_1
                verify_status['gap_expiry'] = now + VERIFY_GAP_TIME
                verify_status['verify_token'] = ""
                verify_status['verified_time'] = now
                await update_verify_status(id, is_verified=True, current_step=1, 
                                         verify1_expiry=verify_status['verify1_expiry'],
                                         gap_expiry=verify_status['gap_expiry'],
                                         verify_token="", verified_time=now)
                await message.reply(f"✅ First verification complete! You now have temporary access.\n\nAccess valid for: {get_exp_time(VERIFY_EXPIRE_1)}", protect_content=False, quote=True)
                return
            
            # STEP 2 verification
            elif step == 1 and token == verify_status['verify_token']:
                verify_status['current_step'] = 2
                verify_status['is_verified'] = True
                verify_status['verify2_expiry'] = now + VERIFY_EXPIRE_2
                verify_status['verify_token'] = ""
                verify_status['verified_time'] = now
                await update_verify_status(id, is_verified=True, current_step=2,
                                         verify2_expiry=verify_status['verify2_expiry'],
                                         verify_token="", verified_time=now)
                await message.reply(f"✅ Second verification complete! Full access unlocked.\n\nAccess valid for: {get_exp_time(VERIFY_EXPIRE_2)}", protect_content=False, quote=True)
                return

        verify_status = await get_verify_status(id)
        step = verify_status['current_step']
        
        if step == 2 and verify_status['verify2_expiry'] > 0 and now >= verify_status['verify2_expiry']:
            # Second verification expired → reset to step 1 and require re-verification
            verify_status['is_verified'] = False
            verify_status['current_step'] = 1
            verify_status['verify2_expiry'] = 0
            verify_status['gap_expiry'] = 0
            await update_verify_status(id, is_verified=False, current_step=1, verify2_expiry=0, gap_expiry=0)
            step = 1

        if step == 1 and verify_status['verify1_expiry'] > 0 and now >= verify_status['verify1_expiry']:
            # First verification expired → reset everything
            verify_status['is_verified'] = False
            verify_status['current_step'] = 0
            verify_status['verify1_expiry'] = 0
            verify_status['gap_expiry'] = 0
            await update_verify_status(id, is_verified=False, current_step=0, verify1_expiry=0, gap_expiry=0)
            step = 0

        elif len(message.text) > 7:
            # Refresh current state
            verify_status = await get_verify_status(id)
            now = time.time()
            step = verify_status['current_step']
            access_allowed = False
            access_type = None  # 'full', 'temporary', or None
            
            # Extract file_id from the base64_string for custom image retrieval
            try:
                base64_string = message.text.split(" ", 1)[1]
                _string = await decode(base64_string)
                argument = _string.split("-")
                
                # Construct file_id based on the argument format
                if len(argument) == 3:
                    # Batch link format: batch-{f_msg_id}-{s_msg_id}
                    start_id = int(int(argument[1]) / abs(client.db_channel.id))
                    end_id = int(int(argument[2]) / abs(client.db_channel.id))
                    file_id_for_image = f"batch-{start_id}-{end_id}"
                elif len(argument) == 2:
                    # Single file link format: get-{msg_id}
                    msg_id = int(int(argument[1]) / abs(client.db_channel.id))
                    file_id_for_image = f"get-{msg_id}"
                else:
                    file_id_for_image = ""
            except:
                file_id_for_image = ""
            
            # Determine access level based on dual verification state
            if step == 2:
                # User is at step 2 - check if step 2 hasn't expired
                if verify_status['verify2_expiry'] > 0 and now < verify_status['verify2_expiry']:
                    access_allowed = True
                    access_type = 'full'
                else:
                    # Step 2 expired, need verification again
                    access_type = 'require_step2'
                    
            elif step == 1:
                # User is at step 1 - check multiple conditions
                if verify_status['verify1_expiry'] > 0 and now >= verify_status['verify1_expiry']:
                    # Step 1 expired completely
                    access_type = 'require_step1'
                elif verify_status['gap_expiry'] > 0 and now < verify_status['gap_expiry']:
                    # Still in gap period, allow temporary access
                    access_allowed = True
                    access_type = 'temporary'
                elif is_dual_verification_enabled() and (verify_status['gap_expiry'] == 0 or now >= verify_status['gap_expiry']):
                    # Gap expired and dual verification is enabled, need step 2
                    access_type = 'require_step2'
                else:
                    # Dual verification disabled or gap not set, allow access
                    access_allowed = True
                    access_type = 'full'
                    
            elif step == 0:
                # Never verified
                access_type = 'require_step1'

            # Handle access based on access_type
            if not access_allowed and IS_VERIFY and access_type:
                if access_type == 'require_step1':
                    token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                    await update_verify_status(id, verify_token=token, is_verified=False, current_step=0)
                    link = await get_shortlink(SHORTLINK_URL_1, SHORTLINK_API_1, f'https://telegram.dog/{client.username}?start=verify_{token}')
                    
                    if link and isinstance(link, str) and link.startswith(('http://', 'https://', 'tg://')):
                        btn = [
                            [InlineKeyboardButton("Click here", url=link)],
                        ]
                        if TUT_VID and isinstance(TUT_VID, str) and TUT_VID.startswith(('http://', 'https://', 'tg://')):
                            btn.append([InlineKeyboardButton('How to use the bot', url=TUT_VID)])
                        
                        # Use the extracted file_id_for_image to get custom image
                        verify_image = await get_verify_image(file_id_for_image)
                        caption_text = f"Your token is expired or not verified. Complete verification to access files.\n\nToken Timeout: {get_exp_time(VERIFY_EXPIRE_1)}"
                        await send_verification_message(message, caption_text, verify_image, InlineKeyboardMarkup(btn))
                    else:
                        await message.reply(f"Your token is expired or not verified. Complete verification to access files.\n\nToken Timeout: {get_exp_time(VERIFY_EXPIRE_1)}\n\nError: Could not generate verification link. Please try again.", protect_content=False, quote=True)
                    return
                
                elif access_type == 'require_step2':
                    token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                    await update_verify_status(id, verify_token=token, is_verified=False, current_step=1)
                    link = await get_shortlink(SHORTLINK_URL_2, SHORTLINK_API_2, f'https://telegram.dog/{client.username}?start=verify_{token}')
                    
                    if link and isinstance(link, str) and link.startswith(('http://', 'https://', 'tg://')):
                        btn = [
                            [InlineKeyboardButton("Click here", url=link)],
                        ]
                        if TUT_VID and isinstance(TUT_VID, str) and TUT_VID.startswith(('http://', 'https://', 'tg://')):
                            btn.append([InlineKeyboardButton('How to use the bot', url=TUT_VID)])
                        
                        # Use the extracted file_id_for_image to get custom image
                        verify_image = await get_verify_image(file_id_for_image)
                        caption_text = f"Complete second verification to continue accessing files.\n\nToken Timeout: {get_exp_time(VERIFY_EXPIRE_2)}"
                        await send_verification_message(message, caption_text, verify_image, InlineKeyboardMarkup(btn))
                    else:
                        await message.reply(f"Complete second verification to continue accessing files.\n\nToken Timeout: {get_exp_time(VERIFY_EXPIRE_2)}\n\nError: Could not generate verification link. Please try again.", protect_content=False, quote=True)
                    return

            # If access is allowed, proceed to decode and send files
            if access_allowed or not IS_VERIFY:
                try:
                    base64_string = message.text.split(" ", 1)[1]
                except:
                    return
                _string = await decode(base64_string)
                argument = _string.split("-")
                if len(argument) == 3:
                    try:
                        start = int(int(argument[1]) / abs(client.db_channel.id))
                        end = int(int(argument[2]) / abs(client.db_channel.id))
                    except:
                        return
                    if start <= end:
                        ids = range(start, end+1)
                    else:
                        ids = []
                        i = start
                        while True:
                            ids.append(i)
                            i -= 1
                            if i < end:
                                break
                elif len(argument) == 2:
                    try:
                        ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                    except:
                        return
                temp_msg = await message.reply("Please wait...")
                try:
                    messages = await get_messages(client, ids)
                except:
                    await message.reply_text("Something went wrong..!")
                    return
                await temp_msg.delete()
                
                snt_msgs = []
                
                for msg in messages:
                    if bool(CUSTOM_CAPTION) & bool(msg.document):
                        caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name)
                    else:
                        caption = "" if not msg.caption else msg.caption.html

                    if DISABLE_CHANNEL_BUTTON:
                        reply_markup = msg.reply_markup
                    else:
                        reply_markup = None

                    try:
                        snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                        await asyncio.sleep(0.5)
                        snt_msgs.append(snt_msg)
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                        snt_msgs.append(snt_msg)
                    except:
                        pass

                SD = await message.reply_text("Baka! Files will be deleted After 600 seconds. Save them to the Saved Message now!")
                await asyncio.sleep(600)

                for snt_msg in snt_msgs:
                    try:
                        await snt_msg.delete()
                        await SD.delete()
                    except:
                        pass

        elif verify_status['is_verified']:
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("About Me", callback_data="about"),
                  InlineKeyboardButton("Close", callback_data="close")]]
            )
            await message.reply_text(
                text=START_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=None if not message.from_user.username else '@' + message.from_user.username,
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                quote=True
            )

        else:
            verify_status = await get_verify_status(id)
            if IS_VERIFY and not verify_status['is_verified']:
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                await update_verify_status(id, verify_token=token, link="")
                link = await get_shortlink(SHORTLINK_URL_1, SHORTLINK_API_1, f'https://telegram.dog/{client.username}?start=verify_{token}')
                
                if link and isinstance(link, str) and link.startswith(('http://', 'https://', 'tg://')):
                    btn = [
                        [InlineKeyboardButton("Click here", url=link)],
                    ]
                    if TUT_VID and isinstance(TUT_VID, str) and TUT_VID.startswith(('http://', 'https://', 'tg://')):
                        btn.append([InlineKeyboardButton('How to use the bot', url=TUT_VID)])
                    
                    file_id = verify_status.get('link', '')
                    verify_image = await get_verify_image(file_id)
                    caption_text = f"Your Ads token is expired, refresh your token and try again.\n\nToken Timeout: {get_exp_time(VERIFY_EXPIRE_1)}\n\nWhat is the token?\n\nThis is an ads token. If you pass 1 ad, you can use the bot for {get_exp_time(VERIFY_EXPIRE_1)} after passing the ad."
                    await send_verification_message(message, caption_text, verify_image, InlineKeyboardMarkup(btn))
                else:
                    await message.reply(f"Your Ads token is expired, refresh your token and try again.\n\nToken Timeout: {get_exp_time(VERIFY_EXPIRE_1)}\n\nWhat is the token?\n\nThis is an ads token. If you pass 1 ad, you can use the bot for {get_exp_time(VERIFY_EXPIRE_1)} after passing the ad.\n\nError: Could not generate verification link. Please try again.", protect_content=False, quote=True)


WAIT_MSG = "<b>ᴡᴏʀᴋɪɴɢ....</b>"

REPLY_ERROR = "<code>Use this command as a reply to any telegram message without any spaces.</code>"


@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [
        [
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink2),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink3),
        ],
        [
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink),
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text = '• ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •',
                    url = f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text = FORCE_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
        reply_markup = InlineKeyboardMarkup(buttons),
        quote = True,
        disable_web_page_preview = True
    )

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} ᴜꜱᴇʀꜱ ᴀʀᴇ ᴜꜱɪɴɢ ᴛʜɪꜱ ʙᴏᴛ")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ᴛɪʟʟ ᴡᴀɪᴛ ʙʀᴏᴏ... </i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except Exception as e:
                unsuccessful += 1
                logging.error(f"Broadcast Error: {e}")
            total += 1
        
        status = f"""<b><u>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴍʏ sᴇɴᴘᴀɪ!!</u>

ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: <code>{total}</code>
ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ: <code>{successful}</code>
ʙʟᴏᴄᴋᴇᴅ ᴜꜱᴇʀꜱ: <code>{blocked}</code>
ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛꜱ: <code>{deleted}</code>
ᴜɴꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ: <code>{unsuccessful}</code></b></b>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
