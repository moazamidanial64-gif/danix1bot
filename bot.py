import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

TOKEN = os.environ.get("BOT_TOKEN")

def start(update, context):
    update.message.reply_text("سلام! لینک یوتیوب بفرست 🎬")

def handle_link(update, context):
    url = update.message.text
    if "youtube.com" in url or "youtu.be" in url:
        context.user_data["url"] = url
        keyboard = [[
            InlineKeyboardButton("🎬 ویدیو", callback_data="video"),
            InlineKeyboardButton("🎵 MP3", callback_data="audio")
        ]]
        update.message.reply_text("چی می‌خوای؟", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        update.message.reply_text("فقط لینک یوتیوب بفرست!")

def handle_choice(update, context):
    query = update.callback_query
    query.answer()
    url = context.user_data.get("url")
    choice = query.data
    query.edit_message_text("داره دانلود میشه... ⏳")
    try:
        if choice == "audio":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "/tmp/%(title)s.%(ext)s",
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
            }
        else:
            ydl_opts = {
                "format": "best[filesize<50M]",
                "outtmpl": "/tmp/%(title)s.%(ext)s",
            }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if choice == "audio":
                filename = filename.rsplit(".", 1)[0] + ".mp3"
        with open(filename, "rb") as f:
            if choice == "audio":
                query.message.reply_audio(f)
            else:
                query.message.reply_video(f)
        os.remove(filename)
    except Exception as e:
        query.message.reply_text(f"خطا: {str(e)}")

updater = Updater(TOKEN)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_link))
dp.add_handler(CallbackQueryHandler(handle_choice))
updater.start_polling()
updater.idle()
