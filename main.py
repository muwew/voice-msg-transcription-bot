import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from transcribe import transcribe_file

# Store user's selected language
user_languages = {}  # {user_id: language_code}


# /start command to choose language
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("English", callback_data="en")],
        [InlineKeyboardButton("Mandarin", callback_data="zh")],
        [InlineKeyboardButton("Spanish", callback_data="es")],
        [InlineKeyboardButton("French", callback_data="fr")],
        [InlineKeyboardButton("Auto-detect", callback_data="auto")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🌐 Please select the language spoken in your voice messages:",
        reply_markup=reply_markup,
    )


# Handle language selection from the buttons
async def handle_language_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    selected_lang = query.data
    user_languages[user_id] = selected_lang

    await query.edit_message_text(
        text=f"✅ Language set to: `{selected_lang}`.\nNow send a voice message to transcribe!",
        parse_mode="Markdown",
    )


# Handle incoming voice messages
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    selected_lang = user_languages.get(user_id, "auto")

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    # Create audio folder if it doesn't exist
    os.makedirs("audio", exist_ok=True)

    # Download the file
    file_path = f"audio/{voice.file_id}.ogg"
    await file.download_to_drive(file_path)

    # Transcribe the file with the selected language
    transcription = transcribe_file(file_path, selected_lang)

    # Add date and time
    timestamp = datetime.now().strftime("%d %b %Y, %H:%M")

    # Build the reply
    reply_text = (
        f"`{transcription}`\n\n"
        f"Date: _{timestamp}_"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
        parse_mode="Markdown",
    )


if __name__ == "__main__":
    import logging
    import dotenv

    dotenv.load_dotenv()
    logging.basicConfig(level=logging.INFO)

    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_language_choice))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("✅ Bot is running...")
    app.run_polling()
