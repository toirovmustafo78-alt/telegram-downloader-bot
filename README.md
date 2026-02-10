# Telegram Video Downloader Bot

Ushbu bot Instagram va YouTubedan videolarni yuklab olish uchun mo'ljallangan.

## Xususiyatlari
- Instagram Reels va Post yuklash
- YouTube Shorts va Video yuklash
- Admin panel (Statistika va Broadcast)
- 24/7 ishlaydi (Render.com orqali)

## O'rnatish
1. Repositoriyani klon qiling.
2. `pip install -r requirements.txt` orqali kutubxonalarni o'rnating.
3. `bot.py` faylidagi `TOKEN` va `ADMIN_ID` ni o'zgartiring.
4. `python bot.py` ni ishga tushiring.

## Hosting
Render.com da `Web Service` sifatida deploy qiling.
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn bot:app`
