
import os
import json
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from bot_core import get_bot_application, TELEGRAM_TOKEN

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# This is crucial for Vercel to pick up the ASGI application
# For @vercel/python, we typically need a function that takes a request and returns a response.
# The structure below is a common pattern for serverless functions handling webhooks.

async def handler(request):
    """
    Vercel serverless function entry point for Telegram webhooks.
    Handles incoming POST requests from Telegram.
    """
    if request.method == "POST":
        try:
            # Get the bot application instance
            application = await get_bot_application()

            # Ensure application.bot is set up for webhook
            # This is critical for the `process_update` to work correctly in a webhook context
            # without polling.
            await application.update_queued_updates()

            # Read the raw request body
            body_bytes = await request.body
            body_str = body_bytes.decode('utf-8')
            update_data = json.loads(body_str)
            
            # Create an Update object from the received JSON
            update = Update.de_json(update_data, application.bot)
            logger.info(f"Received update: {update.update_id}")

            # Process the update
            await application.process_update(update)

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"message": "ok"})
            }
        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"message": "Error processing update"})
            }
    else:
        # Handle GET requests (e.g., for Vercel's health check or initial setup)
        logger.info("Received GET request.")
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "Telegram Bot webhook listener. Send POST requests here."})
        }

# This is required by Vercel to make the `handler` function available as a serverless function.
# For @vercel/python, the entry point function should be directly at the top level of the file
# and is often named `handler` or `vercel_handler`.
