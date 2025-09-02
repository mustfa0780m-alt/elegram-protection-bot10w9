# bot.py
import asyncio
import json
from telethon import TelegramClient, events, types

# ================= إعدادات البوت =================
API_ID = 19544986
API_HASH = "83d3621e6be385938ba3618fa0f0b543"
BOT_TOKEN = "8426678140:AAG3721Hak7V0u_ACZOl2pQHzMgY7Udxk4k"

GROUP_IDS = [2959148009, 1158165922]  # قائمة المجموعات
CHANNEL_ID = 2334004240  # القناة للمراقبة
ADMIN_ID = 5572107425  # صاحب البوت

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ================= ملفات الردود =================
RESPONSES_FILE = "responses.json"

try:
    with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
        responses = json.load(f)
except:
    responses = {}

# ================= متغيرات التحكم =================
MEDIA_BLOCKED = False
RESTRICTED_USERS = set()
BANNED_USERS = set()
PREMIUM_USERS = set()
ADMINS = {ADMIN_ID}
MODERATORS = set()

# ================= دوال مساعدة =================
async def save_responses():
    with open(RESPONSES_FILE, "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)

async def restrict_user(chat_id, user_id):
    try:
        await client.edit_permissions(chat_id, user_id, send_messages=False)
        RESTRICTED_USERS.add(user_id)
    except:
        pass

async def unrestrict_user(chat_id, user_id):
    try:
        await client.edit_permissions(chat_id, user_id, send_messages=True)
        if user_id in RESTRICTED_USERS:
            RESTRICTED_USERS.remove(user_id)
    except:
        pass

async def ban_user(chat_id, user_id):
    try:
        await client.edit_permissions(chat_id, user_id, view_messages=False)
        BANNED_USERS.add(user_id)
    except:
        pass

async def unban_user(chat_id, user_id):
    try:
        await client.edit_permissions(chat_id, user_id, view_messages=True)
        if user_id in BANNED_USERS:
            BANNED_USERS.remove(user_id)
    except:
        pass

# ================= مراقبة الرسائل =================
@client.on(events.NewMessage(chats=GROUP_IDS))
async def handle_new_message(event):
    sender = await event.get_sender()
    user_id = sender.id
    text = event.raw_text

    # ================= الردود المختصرة =================
    if text in responses:
        await event.reply(responses[text])
        return

    # ================= حذف الرسائل الطويلة =================
    if len(text) > 2000:
        await event.delete()
        return

    # ================= حذف الوسائط إذا مغلقة =================
    global MEDIA_BLOCKED
    if MEDIA_BLOCKED and (event.photo or event.video or event.sticker or event.voice or event.gif or event.audio):
        await event.delete()
        return

# ================= أوامر البوت =================
@client.on(events.NewMessage(chats=GROUP_IDS, from_users=ADMINS))
async def admin_commands(event):
    text = event.raw_text
    reply = await event.get_reply_message() if event.is_reply else None
    user_id = reply.sender_id if reply else None

    # ====== القيود ======
    if reply:
        if text == "حظر":
            await ban_user(event.chat_id, user_id)
            await event.reply(f"تم حظر العضو {user_id}")
        elif text == "إلغاء الحظر":
            await unban_user(event.chat_id, user_id)
            await event.reply(f"تم رفع الحظر عن {user_id}")
        elif text == "كتم":
            await restrict_user(event.chat_id, user_id)
            await event.reply(f"تم كتم العضو {user_id}")
        elif text == "إلغاء الكتم":
            await unrestrict_user(event.chat_id, user_id)
            await event.reply(f"تم رفع الكتم عن {user_id}")
        elif text == "رفع طز":
            PREMIUM_USERS.add(user_id)
            await event.reply(f"تم رفع العضو {user_id} عضو مميز")
        elif text == "رفع مشرف":
            MODERATORS.add(user_id)
            await event.reply(f"تم رفع العضو {user_id} مشرف للبوت")
        elif text == "تنزيل مشرف":
            if user_id in MODERATORS:
                MODERATORS.remove(user_id)
                await event.reply(f"تم تنزيل المشرف {user_id} إلى عضو عادي")
        elif text == "تنزيل عضو مميز":
            if user_id in PREMIUM_USERS:
                PREMIUM_USERS.remove(user_id)
                await event.reply(f"تم تنزيل العضو {user_id} من عضو مميز إلى عضو عادي")

    # ====== التحكم بالوسائط ======
    if text == "إغلاق الوسائط":
        MEDIA_BLOCKED = True
        await event.reply("تم إغلاق الوسائط")
    elif text == "فتح الوسائط":
        MEDIA_BLOCKED = False
        await event.reply("تم فتح الوسائط")

    # ====== إضافة رد مختصر ======
    if text == "اضف رد":
        await event.reply("ارسل الاختصار الآن:")

        response = await client.wait_for(events.NewMessage(from_users=ADMINS))
        shortcut = response.raw_text
        await event.reply("ارسل الرد المراد حفظه:")
        response2 = await client.wait_for(events.NewMessage(from_users=ADMINS))
        reply_text = response2.raw_text
        responses[shortcut] = reply_text
        await save_responses()
        await event.reply(f"تم حفظ الرد: {shortcut} -> {reply_text}")

# ================= تشغيل البوت =================
async def main():
    print("🤖 Bot is running...")
    await client.run_until_disconnected()

asyncio.run(main())