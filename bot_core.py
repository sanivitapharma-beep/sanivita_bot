
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update

from database_supabase import Database
from handlers import Handlers

# Load environment variables (ensure this is done once in the entry point)
load_dotenv()

# Configuration variables
TELEGRAM_TOKEN = os.getenv('BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID', '123456789')
# Add any other necessary global configurations here

# Global instances for database and handlers to avoid re-initialization in serverless context
_db_instance = None
_handlers_instance = None
_application_instance = None

def get_db_instance():
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

def get_handlers_instance():
    global _handlers_instance
    if _handlers_instance is None:
        db = get_db_instance()
        _handlers_instance = Handlers(db)
    return _handlers_instance

def setup_handlers(application: Application, handlers: Handlers):
    """Registers all handlers for the bot application."""
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handlers.handle_message
    ))
    application.add_handler(CallbackQueryHandler(handlers.handle_callback_query))

async def get_bot_application() -> Application:
    """Initializes and returns the Telegram Application instance."""
    global _application_instance
    if _application_instance is None:
        if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "ضع_توكن_البوت_هنا":
            print("❌ TELEGRAM_TOKEN is not set!")
            raise ValueError("TELEGRAM_TOKEN environment variable is not set.")

        _application_instance = Application.builder().token(TELEGRAM_TOKEN).build()
        handlers = get_handlers_instance()
        setup_handlers(_application_instance, handlers)

        # Admin user setup (can be moved or adapted if preferred elsewhere)
        try:
            admin_id = int(ADMIN_ID)
            db = get_db_instance()
            db.add_user(admin_id, "admin", "المسؤول", is_admin=True)
            print(f"✅ تم إضافة المسؤول: {admin_id}")
        except ValueError:
            print(f"⚠️ ADMIN_ID غير صحيح: {ADMIN_ID}")
        except Exception as e:
            print(f"⚠️ تعذر إضافة المسؤول: {e}")
        
        await _application_instance.initialize()
        print("✅ Bot Application initialized.")
    return _application_instance

# You can add other utility functions or shared components here
