#!/usr/bin/env python3
"""
Main entry point for running the bot locally.
"""
import os
import asyncio
from bot_core import get_bot_application, TELEGRAM_TOKEN

async def run_bot():
    """Run the bot with polling."""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN not found in environment variables!")
    
    # Get the bot application
    application = await get_bot_application()
    
    # Start the bot with polling
    print("🚀 Starting bot with polling...")
    await application.start()
    await application.updater.start_polling()
    
    # Keep the bot running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n👋 Stopping bot...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        print("✅ Bot stopped.")

if __name__ == "__main__":
    asyncio.run(run_bot())
