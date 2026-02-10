import yt_dlp
import os
import uuid

def download_video(url):
    """
    Instagram yoki YouTube videosini yuklab oladi va fayl yo'lini qaytaradi.
    """
    unique_id = str(uuid.uuid4())
    output_path = f"downloads/{unique_id}.%(ext)s"
    
    # Downloads papkasini yaratish
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
        'max_filesize': 50 * 1024 * 1024,  # 50MB limit (Telegram bot limiti)
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return None

def cleanup_file(filepath):
    """
    Yuklangan faylni o'chirib tashlaydi.
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Faylni o'chirishda xatolik: {e}")
