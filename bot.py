from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import yt_dlp
import os

# টেলিগ্রাম চ্যানেলের ID (আপনার চ্যানেলের থেকে ID সংগ্রহ করুন)
CHANNEL_ID = "@mod_max"

# চ্যানেল জয়েন চেক ফাংশন
def is_user_joined(update: Update) -> bool:
    user_id = update.effective_user.id
    chat_member = update.effective_chat.get_chat_member(user_id)
    return chat_member.status in ['member', 'administrator', 'creator']

# Start কমান্ড
def start(update: Update, context: CallbackContext):
    if not is_user_joined(update):
        update.message.reply_text(
            f"বট ব্যবহার করতে, প্রথমে আমাদের চ্যানেলে যোগ দিন: {CHANNEL_ID}"
        )
        return

    keyboard = [
        [InlineKeyboardButton("ভিডিও", callback_data='video'), InlineKeyboardButton("অডিও", callback_data='audio')],
        [InlineKeyboardButton("Normal", callback_data='normal'), InlineKeyboardButton("Fast VO", callback_data='fast_vo')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("কোন ফাইল ডাউনলোড করতে চান?", reply_markup=reply_markup)

# ডাউনলোড অপশন নির্বাচন হ্যান্ডলার
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data
    if data in ['video', 'audio']:
        context.user_data['type'] = data
        query.edit_message_text("আপনার মোড নির্বাচন করুন।")
    elif data in ['normal', 'fast_vo']:
        context.user_data['mode'] = data
        query.edit_message_text("লিংক পাঠান।")

# ভিডিও/অডিও ডাউনলোড ফাংশন
def download_video_or_audio(url, download_type):
    output_path = "downloads"
    os.makedirs(output_path, exist_ok=True)
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'format': 'bestaudio/best' if download_type == 'audio' else 'best'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(result)

# মেসেজ হ্যান্ডলার (লিংক ডাউনলোড)
def handle_message(update: Update, context: CallbackContext):
    if not is_user_joined(update):
        update.message.reply_text(
            f"বট ব্যবহার করতে, প্রথমে আমাদের চ্যানেলে যোগ দিন: {CHANNEL_ID}"
        )
        return

    url = update.message.text
    download_type = context.user_data.get('type', 'video')
    mode = context.user_data.get('mode', 'normal')

    try:
        if mode == 'normal':
            file_path = download_video_or_audio(url, download_type)
            update.message.reply_text("ডাউনলোড সম্পন্ন! ফাইল পাঠানো হচ্ছে...")
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_path, 'rb'))
        elif mode == 'fast_vo':
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                result = ydl.extract_info(url, download=False)
                download_link = result['url']
                update.message.reply_text(f"ডাউনলোড লিঙ্ক তৈরি হয়েছে:\n[ডাউনলোড করুন]({download_link})", parse_mode='Markdown')
    except Exception as e:
        update.message.reply_text(f"ডাউনলোড করতে সমস্যা হয়েছে: {str(e)}")

# মেইন ফাংশন
def main():
    TOKEN = '7491250770:AAFO63mI635HwA5W4fXmG21u1NV4CWBn2dg'
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()