import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")

# Initialize bot application
application = Application.builder().token(BOT_TOKEN).build()

# Basic command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "مرحباً! أنا بوت سانيفيتا التجريبي.\n"
        "الأوامر المتاحة:\n"
        "/start - بدء البوت\n"
        "/help - المساعدة"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "الأوامر المتاحة:\n"
        "/start - بدء البوت\n"
        "/help - المساعدة"
    )

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))

# Vercel handler function
async def handler(request):
    """Main handler for Vercel serverless function"""
    try:
        # Initialize application
        await application.initialize()

        # Handle POST requests (webhook updates)
        if request.method == "POST":
            body = await request.body()
            data = json.loads(body) if body else {}

            # Process Telegram update
            update = Update.de_json(data, application.bot)
            await application.process_update(update)

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "ok"})
            }
        else:
            # Handle GET requests (health check)
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "Bot is running"})
            }

    except Exception as e:
        logger.error(f"Error in handler: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
