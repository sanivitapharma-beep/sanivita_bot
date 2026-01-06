# دليل النشر على GitHub وربط Supabase

## الخطوة 1: إعداد مشروع على GitHub

1. إنشاء حساب على [GitHub](https://github.com/) إذا لم يكن لديك حساب
2. إنشاء مستودع جديد (New Repository)
3. إعطاء المستودع اسماً مناسباً (مثلاً: sales_bot)
4. اختيار "Public" أو "Private" حسب رغبتك
5. عدم تحديد أي خيارات إضافية (مثل README, .gitignore, License) لأننا أضفناها بالفعل

## الخطوة 2: ربط المشروع بـ GitHub

افتح Terminal في مجلد المشروع ونفذ الأوامر التالية:

```bash
# تهيئة Git
git init

# إضافة الملفات
git add .

# إنشاء أول commit
git commit -m "Initial commit"

# إضافة remote
git remote add origin https://github.com/yourusername/sales_bot.git

# رفع الكود
git push -u origin main
```

## الخطوة 3: إعداد مشروع Supabase

1. إنشاء حساب على [Supabase](https://supabase.com/)
2. إنشاء مشروع جديد (New Project)
3. اختيار اسم المشروع وكلمة المرور
4. انتظار إنشاء المشروع (قد يستغرق بضع دقائق)

## الخطوة 4: إنشاء الجداول في Supabase

1. افتح لوحة تحكم Supabase
2. اذهب إلى SQL Editor
3. انسخ محتوى ملف `supabase_tables.sql`
4. الصقه في SQL Editor
5. اضغط "Run" لإنشاء الجداول

## الخطوة 5: الحصول على بيانات الاتصال بـ Supabase

1. اذهب إلى Settings > API في لوحة تحكم Supabase
2. انسخ:
   - Project URL
   - anon public key (أو service_role key للمزيد من الأمان)

## الخطوة 6: تحديث ملف .env

1. افتح ملف `.env` في المشروع
2. أضف المتغيرات التالية:
```
BOT_TOKEN=your_bot_token_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

## الخطوة 7: رفع التغييرات على GitHub

```bash
git add .
git commit -m "Add Supabase integration"
git push
```

## الخطوة 8: تثبيت المكتبات وتشغيل البوت

```bash
# تثبيت المكتبات
pip install -r requirements.txt

# تشغيل البوت
python run.py
```

## ملاحظات مهمة

- تأكد من عدم رفع ملف `.env` على GitHub (موجود في `.gitignore`)
- يمكنك استخدام Secrets في GitHub Actions لتخزين المتغيرات الحساسة
- للحصول على توكن البوت، تحدث مع @BotFather على Telegram
- تأكد من أن إعدادات الأمان في Supabase مناسبة لاحتياجاتك

## استكشاف الأخطاء

### خطأ: "SUPABASE_URL و SUPABASE_KEY يجب تعريفهما"
- تأكد من إضافة SUPABASE_URL و SUPABASE_KEY في ملف `.env`
- تأكد من أن ملف `.env` موجود في نفس مجلد `main.py`

### خطأ: "فشل الاتصال بقاعدة البيانات"
- تحقق من صحة SUPABASE_URL و SUPABASE_KEY
- تأكد من أن مشروع Supabase نشط
- تحقق من إعدادات الأمان في Supabase

### خطأ: "الجداول غير موجودة"
- تأكد من تنفيذ ملف `supabase_tables.sql` في SQL Editor
- تحقق من أن جميع الجداول تم إنشاؤها بنجاح
