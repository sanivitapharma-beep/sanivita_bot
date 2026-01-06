from telegram import Update
from telegram.ext import ContextTypes
from keyboards import Keyboards
import math

# --- State Constants for the Conversation ---
(
    SELECT_CUSTOMER,
    SELECT_PRODUCT,
    ENTER_QUANTITY,
    ENTER_BONUS,
    ENTER_DISCOUNT,
    ADD_MORE_OR_FINALIZE,
    SELECT_PAYMENT_TYPE,
    ENTER_CASH_AMOUNT,
    ADD_CUSTOMER_NAME,
    ADD_CUSTOMER_PHONE,
    ADD_PRODUCT_NAME,
    ADD_PRODUCT_PRICE,
) = range(12)


class Handlers:
    def __init__(self, database):
        self.db = database
        self.user_states = {}
        self.sale_data = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not self.db.is_user_allowed(user.id):
            self.db.add_user(user.id, user.username, user.full_name)
            await update.message.reply_text(
                f"👋 أهلاً بك {user.full_name}! تم تسجيلك.",
                reply_markup=Keyboards.get_main_menu()
            )
        else:
            await update.message.reply_text(
                f"👋 أهلاً بعودتك {user.full_name}!",
                reply_markup=Keyboards.get_main_menu()
            )
        self._cleanup_state(user.id)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        text = update.message.text
        state = self.user_states.get(user.id)

        # --- Menu Navigation ---
        menu_map = {
            '💰 تسجيل بيع جديد': self.start_new_sale,
            '👥 العملاء': self.show_customer_menu,
            '📦 المنتجات': self.show_product_menu,
            '📊 التقارير': self.show_reports_soon,
            '🔙 القائمة الرئيسية': self.show_main_menu,
            '➕ إضافة عميل جديد': self.start_add_customer,
            '📋 عرض كل العملاء': self.list_all_customers,
            '➕ إضافة منتج جديد': self.start_add_product,
            '📋 عرض كل المنتجات': self.list_all_products,
            '❌ إلغاء': self.cancel_operation,
            '❌ إلغاء الفاتورة بالكامل': self.cancel_operation,
        }
        if text in menu_map:
            await menu_map[text](update, context)
            return

        # --- State-based Handling ---
        if state is None:
            await self.show_main_menu(update, context)
            return

        state_handlers = {
            SELECT_CUSTOMER: self._handle_customer_search,
            SELECT_PRODUCT: self._handle_product_search,
            ENTER_QUANTITY: self._handle_quantity,
            ENTER_BONUS: self._handle_bonus,
            ENTER_DISCOUNT: self._handle_discount,
            ADD_MORE_OR_FINALIZE: self._handle_add_or_finalize,
            SELECT_PAYMENT_TYPE: self._handle_payment_type,
            ENTER_CASH_AMOUNT: self._handle_cash_amount,
            ADD_CUSTOMER_NAME: self._handle_add_customer_name,
            ADD_CUSTOMER_PHONE: self._handle_add_customer_phone,
            ADD_PRODUCT_NAME: self._handle_add_product_name,
            ADD_PRODUCT_PRICE: self._handle_add_product_price,
        }
        handler = state_handlers.get(state)
        if handler:
            await handler(update, context)
        else:
            await self.show_main_menu(update, context)

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = query.from_user
        await query.answer()

        data = query.data
        parts = data.split(':')
        action = parts[0]

        if action == 'page':
            _, data_prefix, page = parts
            page = int(page)
            if data_prefix == 'select_customer':
                await self._list_customers(update, context, page=page)
            elif data_prefix == 'select_product':
                await self._list_products(update, context, page=page)

        elif action == 'select_customer':
            customer_id = int(parts[1])
            customer = self.db.get_customer_by_id(customer_id)
            if not customer:
                await query.edit_message_text("❌ خطأ: العميل غير موجود.")
                self._cleanup_state(user.id)
                return

            self.sale_data[user.id]['customer_id'] = customer_id
            self.sale_data[user.id]['customer_name'] = customer[1]
            await query.edit_message_text(f"👤 تم اختيار العميل: {customer[1]}")
            await self._ask_for_product(update, context)

        elif action == 'select_product':
            product_id = int(parts[1])
            product = self.db.get_product_by_id(product_id)
            if not product:
                await query.edit_message_text("❌ خطأ: المنتج غير موجود.")
                return

            self.sale_data[user.id]['current_item'] = {'product_id': product_id, 'product_name': product[1], 'price_per_unit': product[2]}
            self.user_states[user.id] = ENTER_QUANTITY
            await query.edit_message_text(f"📦 المنتج: {product[1]}\n\nالرجاء إدخال الكمية:")

        elif action in ['cancel_sale', 'cancel_sale_item']:
            await query.edit_message_text("❌ تم الإلغاء.")
            self._cleanup_state(user.id)
            await self.show_main_menu(query, context, is_callback=True)

    # --- MENUS ---
    async def show_main_menu(self, update_or_query, context, is_callback=False):
        text = "📋 القائمة الرئيسية"
        if is_callback:
            await update_or_query.message.reply_text(text, reply_markup=Keyboards.get_main_menu())
        else:
            await update_or_query.message.reply_text(text, reply_markup=Keyboards.get_main_menu())
            
    async def show_customer_menu(self, update, context):
        await update.message.reply_text("👥 إدارة العملاء", reply_markup=Keyboards.get_customer_menu())

    async def show_product_menu(self, update, context):
        await update.message.reply_text("📦 إدارة المنتجات", reply_markup=Keyboards.get_product_menu())
        
    async def show_reports_soon(self, update, context):
        await update.message.reply_text("📊 التقارير ستكون متاحة قريباً بعد تحديثها.", reply_markup=Keyboards.get_main_menu())

    # --- SALE WORKFLOW ---
    async def start_new_sale(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self._cleanup_state(user_id)
        self.sale_data[user_id] = {'items': []}
        self.user_states[user_id] = SELECT_CUSTOMER
        await update.message.reply_text("ابدأ بكتابة اسم العميل للبحث عنه، أو أرسل 'كل العملاء' لعرض القائمة كاملة.", reply_markup=Keyboards.get_cancel_button())

    async def _handle_customer_search(self, update, context):
        query = update.message.text
        search_term = None if query.strip() == 'كل العملاء' else query.strip()
        await self._list_customers(update, context, search_term=search_term)

    async def _list_customers(self, update_or_query, context, page=0, search_term=None):
        customers = self.db.get_customers(search_query=search_term)
        if not customers:
            await update_or_query.message.reply_text("لم يتم العثور على عملاء. حاول مرة أخرى أو أضف عميلاً جديداً.", reply_markup=Keyboards.get_customer_menu())
            self._cleanup_state(update_or_query.effective_user.id)
            return

        keyboard = Keyboards.create_customer_keyboard(customers, page=page)
        text = "👤 اختر العميل من القائمة:"
        if isinstance(update_or_query, Update): # Message
            await update_or_query.message.reply_text(text, reply_markup=keyboard)
        else: # CallbackQuery
            await update_or_query.callback_query.edit_message_text(text, reply_markup=keyboard)

    async def _ask_for_product(self, update, context):
        user_id = update.effective_user.id
        self.user_states[user_id] = SELECT_PRODUCT
        # Show products list directly
        await self._list_products(update, context, search_term=None)

    async def _handle_product_search(self, update, context):
        query = update.message.text
        search_term = None if query.strip() == 'كل المنتجات' else query.strip()
        await self._list_products(update, context, search_term=search_term)

    async def _list_products(self, update_or_query, context, page=0, search_term=None):
        products = self.db.get_products(search_query=search_term)
        if not products:
            await update_or_query.message.reply_text("لم يتم العثور على منتجات.", reply_markup=Keyboards.get_product_menu())
            return
        
        keyboard = Keyboards.create_product_keyboard(products, page=page)
        text = "📦 اختر المنتج:"
        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_text(text, reply_markup=keyboard)
        else:
            await update_or_query.callback_query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_quantity(self, update, context):
        user_id = update.effective_user.id
        try:
            quantity = float(update.message.text)
            if quantity <= 0: raise ValueError
            self.sale_data[user_id]['current_item']['quantity'] = quantity
            self.user_states[user_id] = ENTER_BONUS
            await update.message.reply_text("أدخل الكمية البونص (أو 0):")
        except (ValueError, TypeError):
            await update.message.reply_text("❌ كمية غير صالحة. الرجاء إدخال رقم موجب.")

    async def _handle_bonus(self, update, context):
        user_id = update.effective_user.id
        try:
            bonus = float(update.message.text)
            if bonus < 0: raise ValueError
            self.sale_data[user_id]['current_item']['bonus'] = bonus
            self.user_states[user_id] = ENTER_DISCOUNT
            await update.message.reply_text("أدخل نسبة الخصم (e.g., 10 for 10%, or 0):")
        except (ValueError, TypeError):
            await update.message.reply_text("❌ قيمة غير صالحة. الرجاء إدخال رقم.")

    async def _handle_discount(self, update, context):
        user_id = update.effective_user.id
        try:
            discount = float(update.message.text)
            if not (0 <= discount <= 100): raise ValueError
            self.sale_data[user_id]['current_item']['discount'] = discount
            
            # Add item to the list
            item = self.sale_data[user_id].pop('current_item')
            self.sale_data[user_id]['items'].append(item)
            
            # Show summary and ask for next step
            summary = self._get_current_sale_summary(user_id)
            self.user_states[user_id] = ADD_MORE_OR_FINALIZE
            await update.message.reply_text(summary, reply_markup=Keyboards.get_add_more_or_finalize_keyboard())
        except (ValueError, TypeError):
            await update.message.reply_text("❌ نسبة خصم غير صالحة. الرجاء إدخال رقم بين 0 و 100.")
            
    async def _handle_add_or_finalize(self, update, context):
        text = update.message.text
        if text == '➕ إضافة منتج آخر':
            await self._ask_for_product(update, context)
        elif text == '✅ تسجيل الفاتورة':
            self.user_states[update.effective_user.id] = SELECT_PAYMENT_TYPE
            await update.message.reply_text("اختر طريقة السداد:", reply_markup=Keyboards.get_payment_type_keyboard())
        else:
            await update.message.reply_text("الرجاء الاختيار من الأزرار.")

    async def _handle_payment_type(self, update, context):
        user_id = update.effective_user.id
        text = update.message.text
        if text == '💵 نقدي':
            self.sale_data[user_id]['payment_type'] = 'نقدي'
            self.user_states[user_id] = ENTER_CASH_AMOUNT
            await update.message.reply_text("أدخل المبلغ المدفوع نقداً:")
        elif text == '💳 آجل':
            self.sale_data[user_id]['payment_type'] = 'آجل'
            self.sale_data[user_id]['paid_amount'] = 0
            await self._save_sale(update, context)
        elif text == '🔙 تراجع':
             summary = self._get_current_sale_summary(user_id)
             self.user_states[user_id] = ADD_MORE_OR_FINALIZE
             await update.message.reply_text(summary, reply_markup=Keyboards.get_add_more_or_finalize_keyboard())
        else:
            await update.message.reply_text("الرجاء الاختيار من الأزرار.")

    async def _handle_cash_amount(self, update, context):
        user_id = update.effective_user.id
        try:
            amount = float(update.message.text)
            if amount < 0: raise ValueError
            self.sale_data[user_id]['paid_amount'] = amount
            await self._save_sale(update, context)
        except (ValueError, TypeError):
            await update.message.reply_text("❌ مبلغ غير صالح. الرجاء إدخال رقم موجب.")

    async def _save_sale(self, update, context):
        user_id = update.effective_user.id
        sale_id = self.db.add_sale(self.sale_data[user_id])
        if sale_id:
            summary = self._get_current_sale_summary(user_id, is_final=True)
            final_message = f"✅ تم تسجيل الفاتورة بنجاح!\nرقم الفاتورة: #{sale_id}\n\n{summary}"
            await update.message.reply_text(final_message, reply_markup=Keyboards.get_main_menu())
        else:
            await update.message.reply_text("❌ حدث خطأ أثناء حفظ الفاتورة.", reply_markup=Keyboards.get_main_menu())
        self._cleanup_state(user_id)

    # --- CUSTOMER & PRODUCT MANAGEMENT ---
    async def start_add_customer(self, update, context):
        user_id = update.effective_user.id
        self.user_states[user_id] = ADD_CUSTOMER_NAME
        self.sale_data[user_id] = {} # Use sale_data as temp holder
        await update.message.reply_text("أدخل اسم العميل الجديد:", reply_markup=Keyboards.get_cancel_button())

    async def _handle_add_customer_name(self, update, context):
        user_id = update.effective_user.id
        self.sale_data[user_id]['name'] = update.message.text
        self.user_states[user_id] = ADD_CUSTOMER_PHONE
        await update.message.reply_text("أدخل رقم هاتف العميل (أو 'تخطي'):")

    async def _handle_add_customer_phone(self, update, context):
        user_id = update.effective_user.id
        phone = update.message.text
        self.sale_data[user_id]['phone'] = '' if phone == 'تخطي' else phone
        
        # Save customer
        customer_data = self.sale_data[user_id]
        customer_id = self.db.add_customer(name=customer_data['name'], phone=customer_data['phone'])
        if customer_id:
            await update.message.reply_text(f"✅ تم إضافة العميل '{customer_data['name']}' بنجاح.", reply_markup=Keyboards.get_main_menu())
        else:
            await update.message.reply_text("❌ خطأ: قد يكون اسم العميل موجوداً بالفعل.", reply_markup=Keyboards.get_main_menu())
        self._cleanup_state(user_id)

    async def list_all_customers(self, update, context):
        customers = self.db.get_customers()
        if not customers:
            await update.message.reply_text("لا يوجد عملاء مسجلون حالياً.")
            return
        message = "📋 قائمة العملاء:\n\n"
        for c in customers:
            message += f"👤 {c[1]} (الهاتف: {c[2] or 'N/A'})\n"
        await update.message.reply_text(message)

    async def start_add_product(self, update, context):
        user_id = update.effective_user.id
        self.user_states[user_id] = ADD_PRODUCT_NAME
        self.sale_data[user_id] = {} # Temp holder
        await update.message.reply_text("أدخل اسم المنتج الجديد:", reply_markup=Keyboards.get_cancel_button())

    async def _handle_add_product_name(self, update, context):
        user_id = update.effective_user.id
        self.sale_data[user_id]['name'] = update.message.text
        self.user_states[user_id] = ADD_PRODUCT_PRICE
        await update.message.reply_text("أدخل سعر المنتج:")

    async def _handle_add_product_price(self, update, context):
        user_id = update.effective_user.id
        try:
            price = float(update.message.text)
            if price <= 0: raise ValueError
            self.sale_data[user_id]['price'] = price
            
            # Save product
            product_data = self.sale_data[user_id]
            product_id = self.db.add_product(name=product_data['name'], price=product_data['price'])
            if product_id:
                await update.message.reply_text(f"✅ تم إضافة المنتج '{product_data['name']}' بسعر {price} بنجاح.", reply_markup=Keyboards.get_main_menu())
            else:
                 await update.message.reply_text("❌ خطأ: قد يكون اسم المنتج موجوداً بالفعل.", reply_markup=Keyboards.get_main_menu())
            self._cleanup_state(user_id)
        except (ValueError, TypeError):
            await update.message.reply_text("❌ سعر غير صالح. الرجاء إدخال رقم موجب.")

    async def list_all_products(self, update, context):
        products = self.db.get_products()
        if not products:
            await update.message.reply_text("لا يوجد منتجات مسجلة حالياً.")
            return
        message = "📦 قائمة المنتجات:\n\n"
        for p in products:
            message += f"🏷️ {p[1]} (السعر: {p[2]})\n"
        await update.message.reply_text(message)

    # --- UTILS ---
    async def cancel_operation(self, update, context):
        user_id = update.effective_user.id
        self._cleanup_state(user_id)
        await update.message.reply_text("❌ تم إلغاء العملية.", reply_markup=Keyboards.get_main_menu())

    def _cleanup_state(self, user_id):
        if user_id in self.user_states:
            del self.user_states[user_id]
        if user_id in self.sale_data:
            del self.sale_data[user_id]

    def _get_current_sale_summary(self, user_id, is_final=False):
        data = self.sale_data.get(user_id)
        if not data: return ""
        
        summary = f"**فاتورة العميل: {data.get('customer_name', '')}**\n"
        summary += "--------------------------------\n"
        
        total_amount = 0
        for item in data['items']:
            item_total = item['quantity'] * item['price_per_unit'] * (1 - item['discount']/100)
            total_amount += item_total
            summary += (f"📦 {item['product_name']}\n"
                        f"   - الكمية: {item['quantity']} (+{item.get('bonus',0)} بونص)\n"
                        f"   - السعر: {item['price_per_unit']:.2f}\n"
                        f"   - الخصم: {item['discount']}%\n"
                        f"   - الإجمالي: {item_total:.2f}\n")
        
        summary += "--------------------------------\n"
        summary += f"💰 **الإجمالي المطلوب: {total_amount:.2f}**\n"

        if is_final:
            summary += f"💳 طريقة الدفع: {data.get('payment_type', 'N/A')}\n"
            summary += f"💵 المدفوع: {data.get('paid_amount', 0):.2f}\n"
            summary += f"🧾 المتبقي: {total_amount - data.get('paid_amount', 0):.2f}\n"

        return summary