import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='sales.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        print(f"📁 قاعدة البيانات '{db_name}' جاهزة")

    def create_tables(self):
        """إنشاء الجداول إذا لم تكن موجودة"""
        print("🔍 جاري التحقق من الجداول وتحديثها...")
        # Drop old tables for redesign - this will delete existing sales data
        self.cursor.execute('DROP TABLE IF EXISTS sales')
        self.cursor.execute('DROP TABLE IF EXISTS payments')
        
        # جدول المستخدمين
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                is_admin INTEGER DEFAULT 0,
                registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول العملاء
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                phone TEXT,
                address TEXT,
                notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المنتجات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL
            )
        ''')

        # جدول المبيعات (رأس الفاتورة)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                payment_type TEXT, -- 'نقدي' or 'اجل'
                paid_amount REAL DEFAULT 0,
                notes TEXT,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')

        # جدول أصناف المبيعات (بنود الفاتورة)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                bonus REAL DEFAULT 0,
                discount REAL DEFAULT 0, -- Stored as a percentage, e.g., 10 for 10%
                price_per_unit REAL NOT NULL, -- Price at the time of sale
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        self.conn.commit()
        print("✅ تم إنشاء/تحديث الجداول بنجاح")

    # ========== إدارة المستخدمين ==========
    def add_user(self, telegram_id, username, full_name, is_admin=False):
        """إضافة مستخدم جديد"""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO users (telegram_id, username, full_name, is_admin)
                VALUES (?, ?, ?, ?)
            ''', (telegram_id, username, full_name, 1 if is_admin else 0))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ خطأ في إضافة المستخدم: {e}")
            return False

    def get_user(self, telegram_id):
        """الحصول على بيانات مستخدم"""
        self.cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        return self.cursor.fetchone()

    def is_user_allowed(self, telegram_id):
        """التحقق من صلاحية المستخدم"""
        user = self.get_user(telegram_id)
        return user is not None

    # ========== إدارة العملاء ==========
    def add_customer(self, name, phone="", address="", notes=""):
        """إضافة عميل جديد"""
        try:
            self.cursor.execute('''
                INSERT INTO customers (name, phone, address, notes)
                VALUES (?, ?, ?, ?)
            ''', (name, phone, address, notes))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"❌ خطأ في إضافة العميل: {e}")
            return None

    def get_customers(self, search_query=None):
        """البحث عن عملاء بالاسم أو جلبهم جميعًا"""
        if search_query:
            self.cursor.execute('SELECT * FROM customers WHERE name LIKE ? ORDER BY name', (f'%{search_query}%',))
        else:
            self.cursor.execute('SELECT * FROM customers ORDER BY name')
        return self.cursor.fetchall()
        
    def get_customer_by_id(self, customer_id):
        """الحصول على عميل بالرقم التعريفي"""
        self.cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        return self.cursor.fetchone()

    # ========== إدارة المنتجات ==========
    def add_product(self, name, price):
        """إضافة منتج جديد"""
        try:
            self.cursor.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"❌ خطأ في إضافة المنتج: {e}")
            return None

    def get_products(self, search_query=None):
        """البحث عن منتجات بالاسم أو جلبها جميعًا"""
        if search_query:
            self.cursor.execute('SELECT * FROM products WHERE name LIKE ? ORDER BY name', (f'%{search_query}%',))
        else:
            self.cursor.execute('SELECT * FROM products ORDER BY name')
        return self.cursor.fetchall()

    def get_product_by_id(self, product_id):
        """الحصول على منتج بالرقم التعريفي"""
        self.cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        return self.cursor.fetchone()
        
    # ========== إدارة المبيعات ==========
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
            self.cursor.execute('''
                INSERT INTO sales (customer_id, total_amount, payment_type, paid_amount, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (sale_data['customer_id'], total_amount, sale_data['payment_type'], 
                  sale_data.get('paid_amount', 0), sale_data.get('notes', '')))
            
            sale_id = self.cursor.lastrowid

            # إدراج بنود الفاتورة
            for item in sale_data['items']:
                self.cursor.execute('''
                    INSERT INTO sale_items (sale_id, product_id, quantity, bonus, discount, price_per_unit)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (sale_id, item['product_id'], item['quantity'], item.get('bonus', 0), 
                      item.get('discount', 0), item['price_per_unit']))

            self.conn.commit()
            print(f"✅ تم إضافة عملية بيع #{sale_id} بنجاح")
            return sale_id
        except Exception as e:
            self.conn.rollback()
            print(f"❌ خطأ في إضافة البيع: {e}")
            return None

    def close(self):
        """إغلاق الاتصال بقاعدة البيانات"""
        self.conn.close()

    def get_customers_with_debt(self, search_query=None):
        """الحصول على العملاء للتحصيل"""
        if search_query:
            self.cursor.execute('SELECT * FROM customers WHERE name LIKE ? ORDER BY name', (f'%{search_query}%',))
        else:
            self.cursor.execute('SELECT * FROM customers ORDER BY name')
        return self.cursor.fetchall()

    def get_customer_debt(self, customer_id):
        """حساب دين العميل"""
        self.cursor.execute("""
            SELECT COALESCE(SUM(total_amount - paid_amount), 0) as debt
            FROM sales
            WHERE customer_id = ? AND payment_type = 'اجل' AND paid_amount < total_amount
        """, (customer_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

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
            self.cursor.execute("""
                INSERT INTO sales (customer_id, total_amount, payment_type, paid_amount, notes)
                VALUES (?, 0, 'تحصيل', ?, ?)
            """, (collection_data['customer_id'], collection_data['amount'], collection_data.get('notes', '')))
            
            collection_id = self.cursor.lastrowid
            self.conn.commit()
            print(f"✅ تم إضافة تحصيل #{collection_id} بنجاح")
            return collection_id
        except Exception as e:
            print(f"❌ خطأ في إضافة التحصيل: {e}")
            return None
            
