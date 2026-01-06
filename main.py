
import os
import asyncio
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update

from database_supabase import Database
from handlers import Handlers

# تحميل المتغيرات البيئية
load_dotenv()

# قراءة المتغيرات من .env
TELEGRAM_TOKEN = os.getenv('BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or "ضع_توكن_البوت_هنا"
ADMIN_ID = os.getenv('ADMIN_ID', '123456789')

async def main():
    """الدالة الرئيسية لتشغيل البوت"""
    print("=" * 50)
    print("🚀 جاري تشغيل بوت المبيعات...")
    print("=" * 50)

    local_token = TELEGRAM_TOKEN
    # التحقق من التوكن
    if local_token == "ضع_توكن_البوت_هنا":
        print("\n❌ لم يتم تعيين توكن البوت!")
        print("\n📝 اتبع هذه الخطوات:")
        print("1. افتح Telegram وابحث عن @BotFather")
        print("2. أرسل /newbot واتبع التعليمات")
        print("3. احصل على التوكن")
        print("\n🔧 قم بإضافة التوكن في ملف .env أو أدخله أدناه:")

        token_input = input("أدخل توكن البوت: ").strip()
        if not token_input:
            print("❌ يجب إدخال التوكن!")
            return

        local_token = token_input

    try:
        print("🔧 جاري تهيئة البوت...")

        # إنشاء التطبيق
        application = Application.builder().token(local_token).build()

        # إنشاء قاعدة البيانات والمعالجات
        db = Database()
        handlers = Handlers(db)

        # تسجيل المعالجات
        setup_handlers(application, handlers)

        # إضافة المستخدم المسؤول
        try:
            admin_id = int(ADMIN_ID)
            db.add_user(admin_id, "admin", "المسؤول", is_admin=True)
            print(f"✅ تم إضافة المسؤول: {admin_id}")
        except ValueError:
            print(f"⚠️ ADMIN_ID غير صحيح: {ADMIN_ID}")
        except Exception as e:
            print(f"⚠️ تعذر إضافة المسؤول: {e}")

        print("\n✅ البوت جاهز للعمل!")
        print("📱 افتح تلجرام وابحث عن بوتك")
        print("👉 ابدأ بإرسال /start")
        print("=" * 50)
        print("\n🔄 البوت يعمل... (اضغط Ctrl+C لإيقافه)")

        # تشغيل البوت
        await application.initialize()
        await application.start()
        await application.updater.start_polling()

        # الحفاظ على البوت شغالاً
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        print("\n\n🛑 إيقاف البوت...")
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")

def setup_handlers(application, handlers):
    """تسجيل جميع المعالجات"""

    # معالج الأوامر الأساسية (مثل /start)
    application.add_handler(CommandHandler("start", handlers.start))

    # معالج لجميع الرسائل النصية، يتم توجيهها إلى المعالج الرئيسي
    # الذي بدوره يتصرف بناءً على حالة المستخدم.
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handlers.handle_message
    ))

    # معالج لجميع استعلامات الأزرار المضمنة (Inline Keyboard)
    application.add_handler(CallbackQueryHandler(handlers.handle_callback_query))

def run_bot():
    """تشغيل البوت"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 تم إيقاف البوت")
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")
        print("\n🔧 نصائح استكشاف الأخطاء:")
        print("1. تحقق من توكن البوت في ملف .env")
        print("2. تأكد من اتصال الإنترنت")
        print("3. تأكد من صحة ID الخاص بك")

if __name__ == "__main__":
    run_bot()
