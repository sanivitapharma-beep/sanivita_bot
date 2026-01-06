from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import datetime

# تحميل متغيرات البيئة
load_dotenv()

class Database:
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL و SUPABASE_KEY يجب تعريفهما في ملف .env")

        self.client: Client = create_client(supabase_url, supabase_key)
        print(f"📁 قاعدة البيانات Supabase جاهزة")

    def add_user(self, telegram_id, username, full_name, is_admin=False):
        """إضافة مستخدم جديد"""
        try:
            data = {
                'telegram_id': telegram_id,
                'username': username,
                'full_name': full_name,
                'is_admin': 1 if is_admin else 0
            }
            response = self.client.table('users').insert(data).execute()
            return True
        except Exception as e:
            print(f"❌ خطأ في إضافة المستخدم: {e}")
            return False

    def get_user(self, telegram_id):
        """الحصول على بيانات مستخدم"""
        try:
            response = self.client.table('users').select('*').eq('telegram_id', telegram_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"❌ خطأ في الحصول على المستخدم: {e}")
            return None

    def is_user_allowed(self, telegram_id):
        """التحقق من صلاحية المستخدم"""
        user = self.get_user(telegram_id)
        return user is not None

    def add_customer(self, name, phone="", address="", notes=""):
        """إضافة عميل جديد"""
        try:
            data = {
                'name': name,
                'phone': phone,
                'address': address,
                'notes': notes
            }
            response = self.client.table('customers').insert(data).execute()
            if response.data:
                return response.data[0]['id']
            return None
        except Exception as e:
            print(f"❌ خطأ في إضافة العميل: {e}")
            return None

    def get_customers(self, search_query=None):
        """البحث عن عملاء بالاسم أو جلبهم جميعًا"""
        try:
            if search_query:
                response = self.client.table('customers').select('*').ilike('name', f'%{search_query}%').order('name').execute()
            else:
                response = self.client.table('customers').select('*').order('name').execute()
            return response.data
        except Exception as e:
            print(f"❌ خطأ في الحصول على العملاء: {e}")
            return []

    def get_customer_by_id(self, customer_id):
        """الحصول على عميل بالرقم التعريفي"""
        try:
            response = self.client.table('customers').select('*').eq('id', customer_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"❌ خطأ في الحصول على العميل: {e}")
            return None

    def add_product(self, name, price):
        """إضافة منتج جديد"""
        try:
            data = {
                'name': name,
                'price': price
            }
            response = self.client.table('products').insert(data).execute()
            if response.data:
                return response.data[0]['id']
            return None
        except Exception as e:
            print(f"❌ خطأ في إضافة المنتج: {e}")
            return None

    def get_products(self, search_query=None):
        """البحث عن منتجات بالاسم أو جلبها جميعًا"""
        try:
            if search_query:
                response = self.client.table('products').select('*').ilike('name', f'%{search_query}%').order('name').execute()
            else:
                response = self.client.table('products').select('*').order('name').execute()
            return response.data
        except Exception as e:
            print(f"❌ خطأ في الحصول على المنتجات: {e}")
            return []

    def get_product_by_id(self, product_id):
        """الحصول على منتج بالرقم التعريفي"""
        try:
            response = self.client.table('products').select('*').eq('id', product_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"❌ خطأ في الحصول على المنتج: {e}")
            return None

    def add_sale(self, sale_data):
        """
        إضافة عملية بيع جديدة مع الأصناف الخاصة بها.
        sale_data = {
            'customer_id': 1,
            'payment_type': 'اجل',
            'paid_amount': 0,
            'notes': 'ملاحظات',
            'items': [
                {
                    'product_id': 1,
                    'quantity': 2,
                    'bonus': 0,
                    'discount': 10,
                    'price_per_unit': 150
                },
                ...
            ]
        }
        """
        try:
            # حساب المبلغ الإجمالي للفاتورة
            total_amount = 0
            for item in sale_data['items']:
                price_after_discount = item['price_per_unit'] * (1 - item.get('discount', 0) / 100)
                total_amount += item['quantity'] * price_after_discount

            # إدراج رأس الفاتورة
            sale_data_dict = {
                'customer_id': sale_data['customer_id'],
                'total_amount': total_amount,
                'payment_type': sale_data['payment_type'],
                'paid_amount': sale_data.get('paid_amount', 0),
                'notes': sale_data.get('notes', '')
            }
            response = self.client.table('sales').insert(sale_data_dict).execute()

            if not response.data:
                return None

            sale_id = response.data[0]['id']

            # إدراج بنود الفاتورة
            for item in sale_data['items']:
                item_data = {
                    'sale_id': sale_id,
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'bonus': item.get('bonus', 0),
                    'discount': item.get('discount', 0),
                    'price_per_unit': item['price_per_unit']
                }
                self.client.table('sale_items').insert(item_data).execute()

            print(f"✅ تم إضافة عملية بيع #{sale_id} بنجاح")
            return sale_id
        except Exception as e:
            print(f"❌ خطأ في إضافة البيع: {e}")
            return None

    def get_customers_with_debt(self, search_query=None):
        """الحصول على العملاء للتحصيل"""
        try:
            if search_query:
                response = self.client.table('customers').select('*').ilike('name', f'%{search_query}%').order('name').execute()
            else:
                response = self.client.table('customers').select('*').order('name').execute()
            return response.data
        except Exception as e:
            print(f"❌ خطأ في الحصول على العملاء: {e}")
            return []

    def get_customer_debt(self, customer_id):
        """حساب دين العميل"""
        try:
            # الحصول على جميع المبيعات الأجل للعميل
            response = self.client.table('sales').select('*').eq('customer_id', customer_id).eq('payment_type', 'اجل').execute()

            total_debt = 0
            for sale in response.data:
                debt = sale['total_amount'] - sale['paid_amount']
                if debt > 0:
                    total_debt += debt

            return total_debt
        except Exception as e:
            print(f"❌ خطأ في حساب دين العميل: {e}")
            return 0

    def add_collection(self, collection_data):
        """
        إضافة تحصيل جديد
        collection_data = {
            'customer_id': 1,
            'amount': 100,
            'notes': 'ملاحظات'
        }
        """
        try:
            # إدراج التحصيل في جدول المبيعات كدفعة
            data = {
                'customer_id': collection_data['customer_id'],
                'total_amount': 0,
                'payment_type': 'تحصيل',
                'paid_amount': collection_data['amount'],
                'notes': collection_data.get('notes', '')
            }
            response = self.client.table('sales').insert(data).execute()

            if response.data:
                collection_id = response.data[0]['id']
                print(f"✅ تم إضافة تحصيل #{collection_id} بنجاح")
                return collection_id
            return None
        except Exception as e:
            print(f"❌ خطأ في إضافة التحصيل: {e}")
            return None
