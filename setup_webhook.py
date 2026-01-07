import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_webhook():
    """Setup Telegram bot webhook"""

    # Get environment variables
    bot_token = os.getenv('BOT_TOKEN')
    vercel_url = os.getenv('VERCEL_URL')

    if not bot_token:
        print("❌ BOT_TOKEN not found in environment variables")
        return False

    if not vercel_url:
        print("❌ VERCEL_URL not found in environment variables")
        print("Please provide your Vercel URL (e.g., https://your-project.vercel.app)")
        vercel_url = input("Enter Vercel URL: ").strip()

        if not vercel_url:
            print("❌ Vercel URL is required")
            return False

    # Ensure URL doesn't end with /
    if vercel_url.endswith('/'):
        vercel_url = vercel_url[:-1]

    # Construct webhook URL
    webhook_url = f"{vercel_url}/api/webhook"

    print(f"\n🔧 Setting up webhook...")
    print(f"Webhook URL: {webhook_url}")

    # Set webhook
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"

    try:
        response = requests.post(
            api_url,
            json={
                'url': webhook_url,
                'drop_pending_updates': True
            },
            timeout=30
        )

        result = response.json()

        if result.get('ok'):
            print("✅ Webhook set successfully!")
            print(f"Webhook URL: {webhook_url}")
            return True
        else:
            print(f"❌ Failed to set webhook: {result.get('description')}")
            return False

    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

def get_webhook_info():
    """Get current webhook information"""
    bot_token = os.getenv('BOT_TOKEN')

    if not bot_token:
        print("❌ BOT_TOKEN not found in environment variables")
        return

    api_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"

    try:
        response = requests.get(api_url, timeout=30)
        result = response.json()

        if result.get('ok'):
            info = result.get('result', {})
            print("\n📋 Current Webhook Info:")
            print(f"URL: {info.get('url', 'Not set')}")
            print(f"Pending Updates: {info.get('pending_update_count', 0)}")
            print(f"Last Error: {info.get('last_error_message', 'None')}")
        else:
            print(f"❌ Failed to get webhook info: {result.get('description')}")

    except Exception as e:
        print(f"❌ Error getting webhook info: {e}")

def delete_webhook():
    """Delete current webhook"""
    bot_token = os.getenv('BOT_TOKEN')

    if not bot_token:
        print("❌ BOT_TOKEN not found in environment variables")
        return False

    api_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"

    try:
        response = requests.post(api_url, timeout=30)
        result = response.json()

        if result.get('ok'):
            print("✅ Webhook deleted successfully!")
            return True
        else:
            print(f"❌ Failed to delete webhook: {result.get('description')}")
            return False

    except Exception as e:
        print(f"❌ Error deleting webhook: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Telegram Bot Webhook Setup")
    print("=" * 60)

    print("\nChoose an option:")
    print("1. Setup webhook")
    print("2. Get webhook info")
    print("3. Delete webhook")
    print("4. Exit")

    choice = input("\nEnter your choice (1-4): ").strip()

    if choice == '1':
        setup_webhook()
    elif choice == '2':
        get_webhook_info()
    elif choice == '3':
        delete_webhook()
    elif choice == '4':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")
