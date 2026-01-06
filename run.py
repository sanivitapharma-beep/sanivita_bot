#!/usr/bin/env python3
import os
import sys

def setup_environment():
    """تجهيز البيئة"""
    
    # إنشاء ملف .env إذا لم يكن موجوداً
    if not os.path.exists('.env'):
        print("\n" + "=" * 60)
        print("📝 إعداد ملف البيئة (.env)")
        print("=" * 60)
        
        print("\n🔑 للحصول على توكن البوت:")
        print("1. افتح Telegram وابحث عن @BotFather")
        print("2. أرسل /newbot واتبع التعليمات")
        print("3. احصل على التوكن (يبدأ بأرقام مثل: 1234567890:ABCdefGHIjkl...)\n")
        
        token = input("أدخل توكن البوت: ").strip()
        if not token:
            print("❌ يجب إدخال التوكن!")
            return False
        
        print("\n👑 للحصول على ID الخاص بك:")
        print("1. ابحث عن @userinfobot في Telegram")
        print("2. أرسل /start")
        print("3. انسخ الرقم من 'Id'\n")
        
        admin_id = input("أدخل ID الخاص بك: ").strip()
        if not admin_id:
            print("⚠️ باستخدام ID افتراضي: 123456789")
            admin_id = "123456789"
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(f"TELEGRAM_TOKEN={token}\n")
            f.write(f"ADMIN_ID={admin_id}\n")
        
        print("✅ تم إنشاء ملف .env")
    
    return True

def main():
    print("=" * 60)
    print("🤖 مشغل بوت إدارة المبيعات والتحصيلات")
    print("=" * 60)
    
    # التحقق من المتطلبات
    try:
        import telegram
        import dotenv
        print("✅ المكتبات المطلوبة مثبتة")
    except ImportError:
        print("📦 تثبيت المكتبات المطلوبة...")
        os.system(f"{sys.executable} -m pip install python-telegram-bot python-dotenv")
    
    # إعداد البيئة
    if not setup_environment():
        input("\nاضغط Enter للخروج...")
        return
    
    print("\n" + "=" * 60)
    print("🚀 جاري تشغيل البوت...")
    print("=" * 60 + "\n")
    
    # تشغيل البوت
    try:
        from main import run_bot
        run_bot()
    except KeyboardInterrupt:
        print("\n👋 تم إيقاف البوت")
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")
        print("\n🔧 جرب الخطوات التالية:")
        print("1. تأكد من صحة التوكن")
        print("2. تأكد من اتصال الإنترنت")
        print("3. حذف ملف .env وإعادة التشغيل")
        input("\nاضغط Enter للخروج...")

if __name__ == "__main__":
    main()