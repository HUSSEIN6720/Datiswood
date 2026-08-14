import sqlite3
from datetime import datetime
import flet as ft

DB_NAME = "datis_wood_app.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS production (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, product_name TEXT, maker TEXT,
                qty INTEGER, unit_price REAL, total_price REAL, notes TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, store_name TEXT, product_name TEXT, maker TEXT,
                qty INTEGER, unit_price REAL, sale_type TEXT, interest_pct REAL,
                final_price REAL, notes TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, buyer TEXT, category TEXT, item_name TEXT,
                amount REAL, notes TEXT
            )
        """)
        conn.commit()

init_db()

def main(page: ft.Page):
    page.title = "مدیریت کارگاه داتیس وود"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10

    def show_toast(message: str, is_error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.RED_700 if is_error else ft.colors.GREEN_700
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # 1. TAB: تولید
    prod_date = ft.TextField(label="تاریخ", value=datetime.now().strftime("%Y/%m/%d"), width=160)
    prod_name = ft.TextField(label="نام محصول (مثلاً: کاسه گردو)", expand=True)
    prod_maker = ft.Dropdown(
        label="سازنده",
        options=[ft.dropdown.Option("حسین"), ft.dropdown.Option("محمد"), ft.dropdown.Option("CNC")],
        width=150, value="حسین"
    )
    prod_qty = ft.TextField(label="تعداد", value="1", keyboard_type=ft.KeyboardType.NUMBER, width=120)
    prod_price = ft.TextField(label="ارزش واحد (تومان)", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    prod_notes = ft.TextField(label="توضیحات", expand=True)
    prod_list_view = ft.ListView(expand=True, spacing=10)

    def refresh_prod_list():
        prod_list_view.controls.clear()
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT date, product_name, maker, qty, total_price FROM production ORDER BY id DESC LIMIT 15")
            for r in c.fetchall():
                prod_list_view.controls.append(
                    ft.Card(content=ft.ListTile(
                        title=ft.Text(f"{r[1]} ({r[2]}) - {r[3]} عدد"),
                        subtitle=ft.Text(f"تاریخ: {r[0]} | ارزش کل: {r[4]:,.0f} تومان"),
                        leading=ft.Icon(ft.icons.PRECISION_MANUFACTURING)
                    ))
                )
        page.update()

    def save_production(e):
        if not prod_name.value or not prod_price.value:
            show_toast("لطفاً نام کالا و قیمت را وارد کنید", is_error=True)
            return
        try:
            qty = int(prod_qty.value or 1)
            u_price = float(prod_price.value or 0)
        except ValueError:
            show_toast("تعداد و قیمت باید عدد باشند", is_error=True)
            return
        tot_price = qty * u_price
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO production (date, product_name, maker, qty, unit_price, total_price, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (prod_date.value, prod_name.value, prod_maker.value, qty, u_price, tot_price, prod_notes.value))
            conn.commit()
        prod_name.value, prod_price.value, prod_notes.value = "", "", ""
        prod_qty.value = "1"
        refresh_prod_list()
        refresh_inventory()
        show_toast("تولید با موفقیت ثبت شد")

    tab_production = ft.Column([
        ft.Text("ثبت قطعات تولید شده روزانه", size=18, weight=ft.FontWeight.BOLD),
        ft.Row([prod_date, prod_maker]),
        ft.Row([prod_name]),
        ft.Row([prod_qty, prod_price]),
        ft.Row([prod_notes]),
        ft.ElevatedButton("ثبت در سیستم", icon=ft.icons.ADD, on_click=save_production, style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_700, color="white")),
        ft.Divider(),
        ft.Text("آخرین تولیدات ثبت شده:", weight=ft.FontWeight.BOLD),
        ft.Container(content=prod_list_view, height=250)
    ])

    # 2. TAB: انبار
    inventory_list = ft.ListView(expand=True, spacing=10)

    def refresh_inventory():
        inventory_list.controls.clear()
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            query = """
                SELECT p.product_name, SUM(p.qty) as total_produced,
                COALESCE((SELECT SUM(s.qty) FROM sales s WHERE s.product_name = p.product_name), 0) as total_sold
                FROM production p GROUP BY p.product_name
            """
            c.execute(query)
            for r in c.fetchall():
                p_name, produced, sold = r[0], r[1], r[2]
                stock = produced - sold
                status_color = ft.colors.GREEN_600 if stock > 3 else ft.colors.RED_600
                inventory_list.controls.append(
                    ft.Card(content=ft.Container(padding=10, content=ft.Column([
                        ft.Text(p_name, size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Text(f"کل تولید: {produced}"),
                            ft.Text(f"کل فروش: {sold}"),
                            ft.Text(f"موجودی انبار: {stock}", color=status_color, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ])))
                )
        page.update()

    tab_inventory = ft.Column([
        ft.Text("موجودی زنده انبار کارگاه", size=18, weight=ft.FontWeight.BOLD),
        ft.ElevatedButton("به‌روزرسانی انبار", icon=ft.icons.REFRESH, on_click=lambda e: refresh_inventory()),
        ft.Container(content=inventory_list, height=450)
    ])

    # 3. TAB: فروش
    sale_date = ft.TextField(label="تاریخ", value=datetime.now().strftime("%Y/%m/%d"), width=160)
    sale_store = ft.TextField(label="نام فروشگاه / خریدار", expand=True)
    sale_prod = ft.TextField(label="نام دقیق محصول", expand=True)
    sale_maker = ft.Dropdown(label="سازنده", options=[ft.dropdown.Option("حسین"), ft.dropdown.Option("محمد"), ft.dropdown.Option("CNC")], width=150, value="CNC")
    sale_qty = ft.TextField(label="تعداد", value="1", keyboard_type=ft.KeyboardType.NUMBER, width=120)
    sale_price = ft.TextField(label="قیمت واحد (تومان)", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    sale_type = ft.Dropdown(label="نوع تسویه", options=[ft.dropdown.Option("نقدی"), ft.dropdown.Option("اقساطی"), ft.dropdown.Option("امانی")], value="نقدی", width=150)
    sale_interest = ft.TextField(label="درصد سود اقساط (%)", value="0", keyboard_type=ft.KeyboardType.NUMBER, width=160)

    def save_sale(e):
        if not sale_store.value or not sale_prod.value or not sale_price.value:
            show_toast("لطفاً اطلاعات فروش را کامل کنید", is_error=True)
            return
        try:
            qty = int(sale_qty.value or 1)
            u_price = float(sale_price.value or 0)
            interest = float(sale_interest.value or 0)
        except ValueError:
            show_toast("ورودی‌ها باید عدد باشند", is_error=True)
            return
        base_total = qty * u_price
        final_tot = base_total + (base_total * (interest / 100))
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO sales (date, store_name, product_name, maker, qty, unit_price, sale_type, interest_pct, final_price, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (sale_date.value, sale_store.value, sale_prod.value, sale_maker.value, qty, u_price, sale_type.value, interest, final_tot, f"تسویه: {sale_type.value}"))
            conn.commit()
        sale_store.value, sale_prod.value, sale_price.value = "", "", ""
        sale_qty.value = "1"
        sale_interest.value = "0"
        refresh_inventory()
        load_stats()
        show_toast("فروش با موفقیت ثبت شد")

    tab_sales = ft.Column([
        ft.Text("ثبت فروش و فاکتور مشتریان", size=18, weight=ft.FontWeight.BOLD),
        ft.Row([sale_date, sale_type]),
        ft.Row([sale_store]),
        ft.Row([sale_prod, sale_maker]),
        ft.Row([sale_qty, sale_price]),
        ft.Row([sale_interest]),
        ft.ElevatedButton("ثبت فاکتور فروش", icon=ft.icons.POINT_OF_SALE, on_click=save_sale, style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_700, color="white"))
    ])

    # 4. TAB: خریدهای کارگاه
    exp_date = ft.TextField(label="تاریخ", value=datetime.now().strftime("%Y/%m/%d"), width=160)
    exp_buyer = ft.Dropdown(label="پرداخت‌کننده", options=[ft.dropdown.Option("حسین"), ft.dropdown.Option("محمد")], value="حسین", width=150)
    exp_cat = ft.Dropdown(
        label="دسته‌بندی",
        options=[
            ft.dropdown.Option("چوب و گرده‌بینه"),
            ft.dropdown.Option("ابزار و تیغه CNC"),
            ft.dropdown.Option("رنگ و روغن"),
            ft.dropdown.Option("چسب و مصرفی"),
            ft.dropdown.Option("قبوض و جاری")
        ], expand=True
    )
    exp_item = ft.TextField(label="شرح خرید", expand=True)
    exp_amount = ft.TextField(label="مبلغ (تومان)", keyboard_type=ft.KeyboardType.NUMBER, expand=True)

    def save_expense(e):
        if not exp_amount.value or not exp_item.value:
            show_toast("لطفاً شرح و مبلغ خرید را وارد کنید", is_error=True)
            return
        try:
            amount = float(exp_amount.value)
        except ValueError:
            show_toast("مبلغ باید عدد باشد", is_error=True)
            return
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO expenses (date, buyer, category, item_name, amount, notes) VALUES (?, ?, ?, ?, ?, ?)",
                      (exp_date.value, exp_buyer.value, exp_cat.value, exp_item.value, amount, ""))
            conn.commit()
        exp_item.value, exp_amount.value = "", ""
        load_stats()
        show_toast("هزینه کارگاه ثبت شد")

    tab_expenses = ft.Column([
        ft.Text("ثبت خریدهای کارگاه", size=18, weight=ft.FontWeight.BOLD),
        ft.Row([exp_date, exp_buyer]),
        ft.Row([exp_cat]),
        ft.Row([exp_item]),
        ft.Row([exp_amount]),
        ft.ElevatedButton("ثبت هزینه", icon=ft.icons.SHOPPING_CART, on_click=save_expense, style=ft.ButtonStyle(bgcolor=ft.colors.ORANGE_800, color="white"))
    ])

    # 5. TAB: آمار
    stat_text = ft.Column()

    def load_stats():
        stat_text.controls.clear()
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT SUM(total_price) FROM production")
            res_prod = c.fetchone()
            total_prod_val = res_prod[0] if res_prod and res_prod[0] else 0

            c.execute("SELECT SUM(final_price) FROM sales")
            res_sales = c.fetchone()
            total_sales_val = res_sales[0] if res_sales and res_sales[0] else 0

            c.execute("SELECT buyer, SUM(amount) FROM expenses GROUP BY buyer")
            exp_rows = c.fetchall()

        stat_text.controls.append(
            ft.Card(content=ft.Container(padding=15, content=ft.Column([
                ft.Text("خلاصه عملکرد کارگاه داتیس وود", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(f"ارزش کل تولیدات: {total_prod_val:,.0f} تومان"),
                ft.Text(f"کل درآمد فروش: {total_sales_val:,.0f} تومان", color=ft.colors.GREEN_700, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("خریدهای پرداختی شرکا:"),
                *[ft.Text(f"• {r[0]}: {r[1]:,.0f} تومان") for r in exp_rows]
            ])))
        )
        page.update()

    tab_stats = ft.Column([
        ft.Text("گزارشات و آمار کلی", size=18, weight=ft.FontWeight.BOLD),
        ft.ElevatedButton("محاسبه و بروزرسانی آمار", icon=ft.icons.ANALYTICS, on_click=lambda e: load_stats()),
        stat_text
    ])

    tabs = ft.Tabs(
        selected_index=0, animation_duration=300,
        tabs=[
            ft.Tab(text="تولید", icon=ft.icons.BUILD, content=ft.Container(padding=10, content=tab_production)),
            ft.Tab(text="انبار", icon=ft.icons.INVENTORY, content=ft.Container(padding=10, content=tab_inventory)),
            ft.Tab(text="فروش", icon=ft.icons.ATTACH_MONEY, content=ft.Container(padding=10, content=tab_sales)),
            ft.Tab(text="خریدهای کارگاه", icon=ft.icons.SHOPPING_BAG, content=ft.Container(padding=10, content=tab_expenses)),
            ft.Tab(text="آمار", icon=ft.icons.BAR_CHART, content=ft.Container(padding=10, content=tab_stats)),
        ], expand=1
    )
    page.add(tabs)
    refresh_prod_list()
    refresh_inventory()
    load_stats()

ft.app(target=main)
