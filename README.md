# بوت إدارة المبيعات والتحصيلات

بوت تيليجرام لإدارة المبيعات والتحصيلات مع دعم العملاء والمنتجات.

## المميزات

- تسجيل مبيعات جديدة
- إدارة العملاء
- إدارة المنتجات
- التقارير
- تحصيل الديون من العملاء

## التثبيت

1. استنساخ المستودع:
```bash
git clone https://github.com/yourusername/sales_bot.git
cd sales_bot
```

2. إنشاء بيئة افتراضية:
```bash
python -m venv venv
source venv/bin/activate  # على Linux/Mac
venv\Scripts\activate  # على Windows
```

3. تثبيت المكتبات المطلوبة:
```bash
pip install -r requirements.txt
```

4. إعداد متغيرات البيئة:
```bash
cp .env.example .env
```

5. تعديل ملف `.env` وإضافة:
```
BOT_TOKEN=your_bot_token_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

## الاستخدام

تشغيل البوت:
```bash
python run.py
```

## قاعدة البيانات

يعمل البوت مع Supabase كقاعدة بيانات سحابية. يمكنك إنشاء مشروع جديد على Supabase واستخدام بيانات الاتصال في ملف `.env`.

## الترخيص

MIT License