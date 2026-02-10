import yt_dlp
import os
import uuid
import logging

logger = logging.getLogger(__name__)

def download_video(url):
    """
    Instagram yoki YouTube videosini yuklab oladi va fayl yo'lini qaytaradi.
    """
    unique_id = str(uuid.uuid4())
    # Fayl nomini xavfsiz qilish
    output_dir = 'downloads'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_template = os.path.join(output_dir, f"{unique_id}.%(ext)s")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Telegram mp4 ni yaxshi ko'radi
        'outtmpl': output_template,
        'max_filesize': 48 * 1024 * 1024,  # 48MB (50MB dan biroz kamroq xavfsizlik uchun)
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
        'no_playlist': True,
        # Instagram uchun ba'zi qo'shimcha sozlamalar
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                return None
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        logger.error(f"yt-dlp error: {e}")
        return None

def cleanup_file(filepath):
    """
    Yuklangan faylni o'chirib tashlaydi.
    """
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Fayl o'chirildi: {filepath}")
    except Exception as e:
        logger.error(f"Faylni o'chirishda xatolik: {e}")
