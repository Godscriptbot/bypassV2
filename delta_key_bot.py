import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начало работы"""
    await update.message.reply_text(
        "👋 Привет!\n\n"
        "🔑 Отправьте мне ссылку для получения Delta ключа\n\n"
        "Пример:\n"
        "`https://auth.platorelay.com/a?d=...`\n\n"
        "Бот автоматически пройдёт требования и выдаст вам ключ! ⚡"
    )

def get_delta_key(url: str) -> str:
    """Получить Delta ключ из ссылки"""
    try:
        # Используем headless браузер
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        # Ждём загрузки страницы
        time.sleep(3)
        
        # Ищем кнопку для начала
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button | //a[@role='button'] | //*[@class*='btn']"))
            )
            button.click()
            time.sleep(2)
        except:
            logger.warning("Кнопка не найдена, продолжаем...")
        
        # Ждём загрузки требований
        time.sleep(5)
        
        # Ищем ссылку на требования и открываем их
        try:
            requirements = driver.find_elements(By.TAG_NAME, "a")
            for req in requirements:
                try:
                    req.click()
                    time.sleep(2)
                    # Переходим на новую вкладку если открылась
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(3)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                except:
                    pass
        except:
            pass
        
        time.sleep(3)
        
        # Получаем весь текст со страницы
        page_text = driver.page_source
        
        # Ищем ключ в странице
        if 'delta' in page_text.lower():
            # Пытаемся найти ключ в различных форматах
            import re
            
            # Ищем паттерны ключей
            patterns = [
                r'delta[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)["\']?',
                r'key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
                r'["\']?([a-zA-Z0-9_-]{32,})["\']?',  # 32+ символов - похоже на ключ
            ]
            
            for pattern in patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    key = match.group(1)
                    if len(key) > 10:
                        driver.quit()
                        return key
        
        # Если ключ не найден в исходном коде, ищем на странице
        try:
            key_element = driver.find_element(By.XPATH, "//*[contains(text(), 'key')] | //*[contains(text(), 'Key')]")
            key_text = key_element.text
            driver.quit()
            return key_text.split(":")[-1].strip() if ":" in key_text else key_text
        except:
            pass
        
        driver.quit()
        return None
        
    except Exception as e:
        logger.error(f"Ошибка при получении ключа: {e}")
        return None

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка URL-адреса"""
    url = update.message.text.strip()
    
    # Проверяем, является ли это ссылкой
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text("❌ Пожалуйста, отправьте корректную ссылку (начинающуюся с http:// или https://)")
        return
    
    # Отправляем сообщение о обработке
    processing_msg = await update.message.reply_text("⏳ Получаю ключ Delta... Это может занять 10-15 секунд...")
    
    try:
        # Получаем ключ в отдельном потоке (чтобы не блокировать бота)
        loop = asyncio.get_event_loop()
        key = await loop.run_in_executor(None, get_delta_key, url)
        
        if key:
            await processing_msg.edit_text(
                f"✅ Ключ успешно получен!\n\n"
                f"🔑 <b>Delta Key:</b>\n"
                f"<code>{key}</code>\n\n"
                f"Скопируйте ключ выше ☝️",
                parse_mode="HTML"
            )
        else:
            await processing_msg.edit_text(
                "❌ Не удалось получить ключ.\n\n"
                "Возможные причины:\n"
                "• Некорректная ссылка\n"
                "• Проблема с интернетом\n"
                "• Сервис недоступен\n\n"
                "Попробуйте снова или отправьте другую ссылку."
            )
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await processing_msg.edit_text(
            f"❌ Ошибка при обработке:\n{str(e)}\n\n"
            "Попробуйте снова."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    """Запуск бота"""
    TOKEN = "8671124050:AAFtOokVpRahQg7rRSi7TFWCNrnsYCgw024"
    
    application = Application.builder().token(TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)

    print("🚀 Бот запущен!")
    print("⏳ Ожидание сообщений...")
    
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    main()
