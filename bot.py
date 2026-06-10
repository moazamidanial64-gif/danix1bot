import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک یوتیوب بفرست 🎬")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" in url or "youtu.be" in url:
        context.user_data["url"] = url
        keyboard = [[
            InlineKeyboardButton("🎬 ویدیو", callback_data="video"),
            InlineKeyboardButton("🎵 MP3", callback_data="audio")
        ]]
        await update.message.reply_text("چی می‌خوای؟", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("فقط لینک یوتیوب بفرست!")

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url = context.user_data.get("url")
    choice = query.data
    await query.edit_message_text("داره دانلود میشه... ⏳")
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
                await query.message.reply_audio(f)
            else:
                await query.message.reply_video(f)
        os.remove(filename)
    except Exception as e:
        await query.message.reply_text(f"خطا: {str(e)}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(handle_choice))
app.run_polling()
