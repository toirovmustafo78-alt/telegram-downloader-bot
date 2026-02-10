import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from downloader import download_video, cleanup_file
from database import init_db, add_user, get_all_users, get_stats
from flask import Flask
from threading import Thread

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Bot tokeni
TOKEN = "8366478184:AAGP8zLve0yfm3ABggvKjHvZmcSDkQt4ehQ"
# Admin ID - Foydalanuvchi o'z ID-sini bu yerga qo'yishi kerak
ADMIN_ID = 5621431633 

# Flask server (Render.com da 24/7 ishlash uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    # Render.com PORT muhit o'zgaruvchisini ishlatadi
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.full_name)
    await update.message.reply_text(f"Salom {user.full_name}! Menga Instagram yoki YouTube ssilkasi yuboring, men uni yuklab beraman.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "instagram.com" in url or "youtube.com" in url or "youtu.be" in url:
        msg = await update.message.reply_text("Yuklanmoqda... Iltimos kutib turing.")
        
        # Videoni yuklab olish
        file_path = download_video(url)
        
        if file_path:
            try:
                await update.message.reply_video(video=open(file_path, 'rb'))
                await msg.delete()
            except Exception as e:
                await msg.edit_text(f"Xatolik: Video hajmi juda katta yoki boshqa muammo yuz berdi.")
            finally:
                cleanup_file(file_path)
        else:
            await msg.edit_text("Videoni yuklab bo'lmadi. Ssilka to'g'riligini tekshiring.")
    else:
        await update.message.reply_text("Iltimos, faqat Instagram yoki YouTube ssilkalarini yuboring.")

# Admin Panel funksiyalari
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    stats = get_stats()
    await update.message.reply_text(f"Admin Panel\nJami foydalanuvchilar: {stats}\n\nXabar yuborish uchun: /broadcast [xabar]")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("Xabar matnini yozing: /broadcast Xabar")
        return
    
    text = " ".join(context.args)
    users = get_all_users()
    count = 0
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=text)
            count += 1
        except:
            pass
    await update.message.reply_text(f"Xabar {count} ta foydalanuvchiga yuborildi.")

if __name__ == '__main__':
    # DB ni ishga tushirish
    init_db()
    
    # Flaskni alohida thread da ishga tushirish
    Thread(target=run_flask).start()
    
    # Botni ishga tushirish
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot ishga tushdi...")
    application.run_polling()
