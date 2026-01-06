
from database import Database

def add_default_products():
    """إضافة المنتجات الافتراضية"""
    db = Database()

    products = [
        ("ابسيمارتا شراب", 55),
        ("لابينسيرون شراب", 65.9),
        ("ابينسيكال شراب", 60.9),
        ("جودسبيد كريم", 40),
        ("ابلينسان كبسول", 80),
    ]

    for name, price in products:
        try:
            product_id = db.add_product(name, price)
            if product_id:
                print(f"✅ تم إضافة المنتج: {name} بسعر {price} جنيه")
            else:
                print(f"⚠️ المنتج موجود بالفعل: {name}")
        except Exception as e:
            print(f"❌ خطأ في إضافة المنتج {name}: {e}")

    print("\n✅ تم الانتهاء من إضافة المنتجات الافتراضية")

if __name__ == "__main__":
    add_default_products()
