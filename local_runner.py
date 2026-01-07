
import asyncio
import os
from dotenv import load_dotenv
from bot_core import get_bot_application

# تحميل المتغيرات البيئية
load_dotenv()

async def main_polling():
    """الدالة الرئيسية لتشغيل البوت بوضع البولينج"""
    print("=" * 50)
    print("🚀 جاري تشغيل بوت المبيعات بوضع البولينج...")
    print("=" * 50)

    try:
        application = await get_bot_application()

        print("\n✅ البوت جاهز للعمل!")
        print("📱 افتح تلجرام وابحث عن بوتك")
        print("👉 ابدأ بإرسال /start")
        print("=" * 50)
        print("\n🔄 البوت يعمل... (اضغط Ctrl+C لإيقافه)")

        # تشغيل البوت بوضع البولينج
        await application.start()
        await application.updater.start_polling()

        # الحفاظ على البوت شغالاً
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        print("\n\n🛑 إيقاف البوت...")
    except ValueError as ve:
        print(f"\n❌ خطأ في الإعدادات: {ve}")
        print("\n🔧 نصائح استكشاف الأخطاء:")
        print("1. تأكد من تعيين TELEGRAM_TOKEN في ملف .env")
    except Exception as e:
        print(f"\n❌ حدث خطأ غير متوقع: {e}")
        print("\n🔧 نصائح استكشاف الأخطاء:")
        print("1. تحقق من توكن البوت في ملف .env")
        print("2. تأكد من اتصال الإنترنت")
        print("3. تأكد من صحة ID الخاص بك")

if __name__ == "__main__":
    try:
        asyncio.run(main_polling())
    except KeyboardInterrupt:
        print("\n\n👋 تم إيقاف البوت")
    except Exception as e:
        print(f"\n❌ حدث خطأ أثناء تشغيل البوت: {e}")
