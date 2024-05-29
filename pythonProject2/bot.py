import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
from database import app, db, User, Products, UserChat
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация бота
bot = Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Состояния для ConversationHandler
LOGIN = range(1)

# Функция для команды /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот для отслеживания срока годности ваших продуктов. Введите команду /login для авторизации.')

# Функция для команды /login
def login(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Пожалуйста, введите ваш логин:')
    return LOGIN

# Функция для получения логина пользователя
def received_login(update: Update, context: CallbackContext) -> int:
    user_login = update.message.text
    chat_id = update.message.chat_id

    with app.app_context():
        user = User.query.filter_by(login=user_login).first()
        if user:
            user_chat = UserChat.query.filter_by(login=user_login).first()
            if user_chat:
                user_chat.chat_id = str(chat_id)
            else:
                user_chat = UserChat(chat_id=str(chat_id), login=user_login)
                db.session.add(user_chat)
            db.session.commit()
            update.message.reply_text('Вы успешно авторизованы. Вы будете получать уведомления о продуктах с истекающим сроком годности.')
        else:
            update.message.reply_text('Логин не найден. Пожалуйста, попробуйте еще раз.')
            return LOGIN

    return ConversationHandler.END

# Функция для отмены авторизации
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Авторизация отменена.')
    return ConversationHandler.END

# Функция для проверки сроков годности
def check_expiration():
    logger.info("Запуск проверки сроков годности продуктов...")
    with app.app_context():
        user_chats = UserChat.query.all()
        now = datetime.now()
        warning_period = now + timedelta(days=1)  # Определяем срок предупреждения за 3 дня до истечения срока годности

        for user_chat in user_chats:
            user = User.query.filter_by(login=user_chat.login).first()
            if user:
                expiring_products = [product for product in user.products if product.death_date <= warning_period]
                if expiring_products:
                    message = "У вас следующие продукты скоро истекут:\n"
                    for product in expiring_products:
                        message += f"- {product.name} (до {product.death_date})\n"
                    logger.info(f"Отправка сообщения пользователю {user_chat.login}: {message}")
                    bot.send_message(chat_id=user_chat.chat_id, text=message)

# Настройка планировщика
scheduler = BackgroundScheduler()
timezone = pytz.timezone('Europe/Moscow')
scheduler.add_job(check_expiration, 'cron', hour=9, minute=00, timezone=timezone)
scheduler.start()

# Настройка обработчиков команд
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('login', login)],
    states={
        LOGIN: [MessageHandler(Filters.text & ~Filters.command, received_login)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(conv_handler)

# Запуск бота
def run_bot():
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    run_bot()
