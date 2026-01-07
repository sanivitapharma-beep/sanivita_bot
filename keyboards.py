from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

class Keyboards:
    @staticmethod
    def get_main_menu():
        keyboard = [
            ['💰 تسجيل بيع جديد', '👥 العملاء'],
            ['📊 التقارير', '💵 تحصيل جديد']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def get_report_menu():
        keyboard = [
            ['📅 تقرير اليوم', '🈷️ تقرير الشهر'],
            ['🔙 القائمة الرئيسية']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def get_customer_menu():
        keyboard = [
            ['➕ إضافة عميل جديد', '📋 عرض كل العملاء'],
            ['🔙 القائمة الرئيسية']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def get_product_menu():
        keyboard = [
            ['➕ إضافة منتج جديد', '📋 عرض كل المنتجات'],
            ['🔙 القائمة الرئيسية']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def get_cancel_button():
        return ReplyKeyboardMarkup([['❌ إلغاء']], resize_keyboard=True)

    @staticmethod
    def get_yes_no():
        return ReplyKeyboardMarkup([['✅ نعم', '❌ لا']], resize_keyboard=True)
    
    # --- Dynamic Keyboards for Sales Flow ---

    @staticmethod
    def _create_paginated_keyboard(items, page, page_size, data_prefix, back_callback):
        """Helper function to create paginated inline keyboards."""
        keyboard = []
        start_index = page * page_size
        end_index = start_index + page_size
        
        # Create a button for each item on the current page
        for item_id, item_name in items[start_index:end_index]:
            keyboard.append([InlineKeyboardButton(item_name, callback_data=f'{data_prefix}:{item_id}')])

        # Pagination controls
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f'page:{data_prefix}:{page-1}'))
        if end_index < len(items):
            nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f'page:{data_prefix}:{page+1}'))
        
        if nav_buttons:
            keyboard.append(nav_buttons)

        keyboard.append([InlineKeyboardButton("🔙 إلغاء", callback_data=back_callback)])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_customer_keyboard(customers, page=0, page_size=5):
        """Creates a paginated inline keyboard for customers."""
        # customers is a list of dictionaries or tuples
        customer_list = []
        for c in customers:
            if isinstance(c, dict):
                customer_list.append((c['id'], c['name']))
            else:
                customer_list.append((c[0], c[1]))
        return Keyboards._create_paginated_keyboard(
            items=customer_list,
            page=page,
            page_size=page_size,
            data_prefix='select_customer',
            back_callback='cancel_sale'
        )

    @staticmethod
    def create_product_keyboard(products, page=0, page_size=5):
        """Creates a paginated inline keyboard for products."""
        # products is a list of dictionaries or tuples
        product_list = []
        for p in products:
            if isinstance(p, dict):
                product_list.append((p['id'], f"{p['name']} (السعر: {p['price']})"))
            else:
                product_list.append((p[0], f"{p[1]} (السعر: {p[2]})"))
        return Keyboards._create_paginated_keyboard(
            items=product_list,
            page=page,
            page_size=page_size,
            data_prefix='select_product',
            back_callback='cancel_sale_item' # Go back to previous step
        )

    @staticmethod
    def get_add_more_or_finalize_keyboard():
        """Keyboard for adding another item or finalizing the sale."""
        keyboard = [
            ['✅ تسجيل الفاتورة', '➕ إضافة منتج آخر'],
            ['❌ إلغاء الفاتورة بالكامل']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
    @staticmethod
    def get_payment_type_keyboard():
        """Keyboard for choosing cash or credit."""
        keyboard = [
            ['💵 نقدي', '💳 آجل'],
            ['🔙 تراجع']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
