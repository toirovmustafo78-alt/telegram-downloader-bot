import os
import logging
import asyncio
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from downloader import download_video, cleanup_file
from database import init_db, add_user, get_all_users, get_stats
from flask import Flask
from threading import Thread

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot tokeni
TOKEN = "8366478184:AAGP8zLve0yfm3ABggvKjHvZmcSDkQt4ehQ"
# Admin ID - Iltimos, o'zingizning ID-ingizni bu yerga yozing
ADMIN_ID = 8555950441 

# Flask server (Render.com da 24/7 ishlash uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.full_name)
    await update.message.reply_text(
        f"Salom {user.full_name}! 👋\n\n"
        "Menga Instagram Reels yoki YouTube ssilkasi yuboring, men uni sizga yuklab beraman.\n\n"
        "Bot 24/7 rejimida ishlaydi! ✅"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url:
        return

    if "instagram.com" in url or "youtube.com" in url or "youtu.be" in url:
        msg = await update.message.reply_text("⏳ Videoni qayta ishlayapman... Iltimos kutib turing.")
        
        # Videoni yuklab olish
        try:
            file_path = await asyncio.to_thread(download_video, url)
            
            if file_path and os.path.exists(file_path):
                try:
                    await update.message.reply_video(
                        video=open(file_path, 'rb'),
                        caption="✅ Yuklab olindi! @saved_insta_bot ga o'xshash bot."
                    )
                    await msg.delete()
                except Exception as e:
                    logger.error(f"Video yuborishda xato: {e}")
                    await msg.edit_text("❌ Xatolik: Video hajmi Telegram limitidan (50MB) katta bo'lishi mumkin.")
                finally:
                    cleanup_file(file_path)
            else:
                await msg.edit_text("❌ Videoni yuklab bo'lmadi. Ssilka noto'g'ri yoki video yopiq (private) bo'lishi mumkin.")
        except Exception as e:
            logger.error(f"Download error: {e}")
            await msg.edit_text("❌ Yuklash jarayonida texnik xatolik yuz berdi.")
    else:
        await update.message.reply_text("⚠️ Iltimos, faqat Instagram yoki YouTube ssilkalarini yuboring.")

# Admin Panel
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    stats = get_stats()
    await update.message.reply_text(
        f"📊 *Admin Panel*\n\n"
        f"👥 Jami foydalanuvchilar: {stats}\n\n"
        "Xabar yuborish uchun: `/broadcast [xabar]`",
        parse_mode='Markdown'
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("📝 Xabar matnini yozing: `/broadcast Salom hammaga`", parse_mode='Markdown')
        return
    
    text = " ".join(context.args)
    users = get_all_users()
    count = 0
    
    status_msg = await update.message.reply_text(f"🚀 Xabar {len(users)} ta foydalanuvchiga yuborilmoqda...")
    
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=text)
            count += 1
            await asyncio.sleep(0.05) # Telegram flood limitdan qochish
        except Exception:
            continue
            
    await status_msg.edit_text(f"✅ Xabar {count} ta foydalanuvchiga muvaffaqiyatli yuborildi.")

if __name__ == '__main__':
    # Ma'lumotlar bazasini yaratish
    init_db()
    
    # Flaskni alohida oqimda ishga tushirish (Render.com portni band qilishi uchun)
    Thread(target=run_flask, daemon=True).start()
    
    # Botni ishga tushirish
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot ishga tushdi...")
    application.run_polling()
