from telegram import Update
from telegram.ext import ContextTypes
import pandas as pd
from datetime import datetime, timedelta

class AdminCommands:
    def __init__(self, database):
        self.db = database
    
    async def export_to_excel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تصدير البيانات إلى Excel"""
        user_id = update.effective_user.id
        
        # التحقق من الصلاحيات
        user = self.db.get_user(user_id)
        if not user or not user[4]:  # العمود 4 هو is_admin
            await update.message.reply_text("⛔ هذا الأمر للمسؤولين فقط!")
            return
        
        # جلب جميع المبيعات
        sales = self.db.get_sales()
        
        if not sales:
            await update.message.reply_text("📭 لا توجد بيانات للتصدير!")
            return
        
        # تحويل إلى DataFrame
        df = pd.DataFrame(sales, columns=[
            'ID', 'Product', 'Quantity', 'Price', 'Total', 
            'Customer', 'Phone', 'Date', 'Notes', 
            'Payment Method', 'Is Paid'
        ])
        
        # حفظ في ملف Excel
        filename = f"sales_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        
        # إرسال الملف
        with open(filename, 'rb') as file:
            await update.message.reply_document(
                document=file,
                caption="📊 تصدير بيانات المبيعات"
            )
    
    async def add_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إضافة مستخدم جديد"""
        user_id = update.effective_user.id
        
        # التحقق من الصلاحيات
        user = self.db.get_user(user_id)
        if not user or not user[4]:
            await update.message.reply_text("⛔ هذا الأمر للمسؤولين فقط!")
            return
        
        # التحقق من وجود ID المستخدم في الرسالة
        if not context.args:
            await update.message.reply_text(
                "📝 استخدام الأمر:\n"
                "/add_user <user_id> <username> <full_name>\n\n"
                "مثال:\n"
                "/add_user 123456789 johndoe \"John Doe\""
            )
            return
        
        try:
            new_user_id = int(context.args[0])
            username = context.args[1] if len(context.args) > 1 else ""
            full_name = context.args[2] if len(context.args) > 2 else ""
            
            if self.db.add_user(new_user_id, username, full_name):
                await update.message.reply_text(f"✅ تم إضافة المستخدم {full_name} بنجاح!")
            else:
                await update.message.reply_text("❌ حدث خطأ في إضافة المستخدم!")
                
        except ValueError:
            await update.message.reply_text("⚠️ الرجاء إدخال ID صحيح!")
    
    async def backup_database(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إنشاء نسخة احتياطية"""
        user_id = update.effective_user.id
        
        # التحقق من الصلاحيات
        user = self.db.get_user(user_id)
        if not user or not user[4]:
            await update.message.reply_text("⛔ هذا الأمر للمسؤولين فقط!")
            return
        
        filename = f"sales_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        # نسخ قاعدة البيانات
        import shutil
        shutil.copy2('sales.db', filename)
        
        # إرسال الملف
        with open(filename, 'rb') as file:
            await update.message.reply_document(
                document=file,
                caption="💾 نسخة احتياطية من قاعدة البيانات"
            )
