import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ссылка на получение ключа Delta
DELTA_KEY_URL = "https://auth.platorelay.com/a?d=3aXUTc4Msm0v59ga2Rr4q9i0lbY7fPCSscEMmndc6WpPuhK9DHdAseJ0WfUY1dVjSaedLVexSVCoablpkHy3Cj3cX2cJBTk5oKvZbAq1JwA59ST2TqvqR1Q58qqvRbrpJk4zSYbjgcfnWD6jgKHq2oYsFQYW57K6cG9K2msxG33sYrEDw5rUokE5fCu4S9kT7h8ESKLb9p5zlEGSzYC7sfd6u6j6wsh0kxx2j6vpPem9XP6QYlsRCCB3wVRXLppTudo4VeRO4vgaPEg7TaKzxORYSqyAWPhiG4qBV67QOHhhcgrTwjRtE3y0luizaDZNeGLDx77KOgVepYGduocdckvihVjnjecicRe8mq42yWpmDrOyoS77qAndrfiqkj4rK0zxxrQGOJ4IHtTafQxWJOYwvFS54kwJLuE5GuyxC5pfqyblxU1zUrK5tdHxbNE1dzaH3yZiK3BEfAvzgwUKi9iOaDTd6uOkABs"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Создаем клавиатуру с кнопкой
    keyboard = [
        [InlineKeyboardButton("🔑 Получить ключ Delta", url=DELTA_KEY_URL)],
        [InlineKeyboardButton("ℹ️ О боте", callback_data='about')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        "🤖 Я помогу вам получить ключ Delta для PlatoRelay.\n\n"
        "Нажмите кнопку ниже, чтобы получить доступ:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    keyboard = [
        [InlineKeyboardButton("🔑 Получить ключ Delta", url=DELTA_KEY_URL)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    help_text = (
        "📖 <b>Команды бота:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Справка\n"
        "/key - Получить ссылку на ключ\n\n"
        "Просто нажмите нужную кнопку или используйте команды!"
    )
    
    await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='HTML')

async def get_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /key"""
    keyboard = [
        [InlineKeyboardButton("🔑 Получить ключ Delta", url=DELTA_KEY_URL)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔐 Ваша ссылка для получения ключа Delta готова!\n\n"
        "Нажмите на кнопку ниже:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'about':
        keyboard = [
            [InlineKeyboardButton("🔑 Получить ключ Delta", url=DELTA_KEY_URL)],
            [InlineKeyboardButton("⬅️ Назад", callback_data='back')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        about_text = (
            "ℹ️ <b>О боте</b>\n\n"
            "Этот бот помогает вам легко получить ключ Delta для платформы PlatoRelay.\n\n"
            "✨ <b>Возможности:</b>\n"
            "• Быстрое получение ключей\n"
            "• Удобный интерфейс\n"
            "• Поддержка в любое время\n\n"
            "Версия: 1.0"
        )
        
        await query.edit_message_text(
            about_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif query.data == 'back':
        keyboard = [
            [InlineKeyboardButton("🔑 Получить ключ Delta", url=DELTA_KEY_URL)],
            [InlineKeyboardButton("ℹ️ О боте", callback_data='about')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👋 Выберите действие:",
            reply_markup=reply_markup
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    """Запуск бота"""
    # Замените на ваш токен от BotFather
    TOKEN = "YOUR_BOT_TOKEN_HERE"
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("key", get_key))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    print("🚀 Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()
