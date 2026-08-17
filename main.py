import flet as ft
from datetime import datetime

def main(page: ft.Page):
    page.title = "حسابداری و مدیریت کارگاه داتیس وود"
    page.theme_mode = "light"
    page.rtl = True
    page.scroll = "auto"
    page.padding = 10

    # لوگوی اصلی برنامه
    logo = ft.Image(src="assets/logo.png", width=110, height=65, fit="contain")

    # دادگان متغیر در حافظه (پایگاه داده موقت)
    inventory_data = {}  # انبار کالاها: {"نام کالا": تعداد}
    production_logs = [] # گزارش تولید روزانه
    sales_logs = []      # گزارش فروش
    purchase_logs = []   # گزارش خریدهای کارگاه

    # ---------------------------------------------------------
    # بخش ۱: تولید روزانه
    # ---------------------------------------------------------
    prod_name = ft.TextField(label="نوع محصول تولید شده", width=310, height=48)
    prod_maker = ft.Dropdown(
        label="کی تولید کرده؟",
        width=310,
        options=[
            ft.dropdown.Option("حسین"),
            ft.dropdown.Option("محمد"),
            ft.dropdown.Option("CNC"),
        ],
        value="حسین"
    )
    prod_date = ft.TextField(label="تاریخ تولید", value=datetime.now().strftime("%Y/%m/%d"), width=310, height=48)
    prod_qty = ft.TextField(label="مقدار / تعداد تولید", width=310, height=48, keyboard_type="number")
    prod_list_ui = ft.Column()

    def add_production(e):
        if prod_name.value and prod_qty.value:
            try:
                qty = int(prod_qty.value)
                item = prod_name.value.strip()
                maker = prod_maker.value
                date = prod_date.value

                # اضافه به انبار
                inventory_data[item] = inventory_data.get(item, 0) + qty
                
                # ثبت در گزارش
                production_logs.append({"item": item, "maker": maker, "qty": qty, "date": date})

                # بروزرسانی لیست نمایش تولید
                prod_list_ui.controls.insert(0, 
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"{item} ({qty} عدد)", weight="bold"),
                                ft.Text(f"سازنده: {maker} | تاریخ: {date}", size=11, color="grey700")
                            ]),
                            ft.Icon(name="check_circle", color="green")
                        ], alignment="space_between"),
                        padding=8, bgcolor="green50", border_radius=6
                    )
                )
                prod_name.value = ""
                prod_qty.value = ""
                update_inventory_ui()
                update_analytics_ui()
                page.update()
            except ValueError:
                pass

    tab_production = ft.Column([
        prod_name, prod_maker, prod_date, prod_qty,
        ft.ElevatedButton("ثبت تولید روزانه", on_click=add_production, style=ft.ButtonStyle(bgcolor="green800", color="white")),
        ft.Divider(),
        ft.Text("آخرین تولیدات ثبت شده:", weight="bold"),
        prod_list_ui
    ], horizontal_alignment="center")

    # ---------------------------------------------------------
    # بخش ۲: انبار تولید
    # ---------------------------------------------------------
    inventory_list_ui = ft.Column()

    def update_inventory_ui():
        inventory_list_ui.controls.clear()
        if not inventory_data:
            inventory_list_ui.controls.append(ft.Text("انبار در حال حاضر خالی است.", color="grey"))
        else:
            for item, qty in inventory_data.items():
                inventory_list_ui.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(item, weight="bold", size=15),
                            ft.Text(f"موجودی: {qty} عدد", weight="bold", color="blue800" if qty > 0 else "red")
                        ], alignment="space_between"),
                        padding=10, bgcolor="grey100", border_radius=8
                    )
                )

    tab_inventory = ft.Column([
        ft.Text("موجودی فعلی انبار کالاها", size=16, weight="bold", color="blueGrey900"),
        ft.Divider(),
        inventory_list_ui
    ], horizontal_alignment="center")

    # ---------------------------------------------------------
    # بخش ۳ و ۶: فروش و پرینت فاکتور
    # ---------------------------------------------------------
    sale_customer = ft.TextField(label="نام مشتری", width=310, height=48)
    sale_item = ft.TextField(label="نام کالا", width=310, height=48)
    sale_qty = ft.TextField(label="تعداد", width=310, height=48, keyboard_type="number")
    sale_price = ft.TextField(label="مبلغ کل (تومان)", width=310, height=48, keyboard_type="number")
    sale_payment_type = ft.Dropdown(
        label="نوع تسویه مالی",
        width=310,
        options=[
            ft.dropdown.Option("نقدی"),
            ft.dropdown.Option("کارت به کارت"),
            ft.dropdown.Option("چک"),
            ft.dropdown.Option("اقساطی"),
        ],
        value="کارت به کارت"
    )
    sales_list_ui = ft.Column()

    def add_sale(e):
        if sale_customer.value and sale_item.value and sale_price.value:
            try:
                qty = int(sale_qty.value or 1)
                price = int(sale_price.value.replace(",", ""))
                item = sale_item.value.strip()
                customer = sale_customer.value
                p_type = sale_payment_type.value

                # کسر از انبار
                inventory_data[item] = inventory_data.get(item, 0) - qty

                sales_logs.append({"customer": customer, "item": item, "qty": qty, "price": price, "type": p_type, "date": datetime.now().strftime("%Y/%m/%d")})

                sales_list_ui.controls.insert(0,
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"مشتری: {customer} | {item} ({qty} عدد)", weight="bold"),
                                ft.Text(f"تسویه: {p_type} | مبلغ: {price:,} تومان", size=12, color="blue800")
                            ]),
                            ft.Icon(name="shopping_cart", color="blue")
                        ], alignment="space_between"),
                        padding=8, bgcolor="blue50", border_radius=6
                    )
                )
                update_inventory_ui()
                update_analytics_ui()
                page.update()
            except ValueError:
                pass

    def print_invoice_dialog(e):
        if not sales_logs:
            return
        
        last_sale = sales_logs[0]
        
        def close_dialog(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Column([
                ft.Image(src="assets/logo.png", width=100, height=60, fit="contain"),
                ft.Text("فاکتور فروش صنایع چوب داتیس وود", size=15, weight="bold", color="green800"),
                ft.Divider()
            ], horizontal_alignment="center"),
            content=ft.Column([
                ft.Text(f"تاریخ: {last_sale['date']}"),
                ft.Text(f"خریدار: {last_sale['customer']}", weight="bold"),
                ft.Divider(),
                ft.Row([ft.Text(f"شرح کالا: {last_sale['item']}"), ft.Text(f"تعداد: {last_sale['qty']}")], alignment="space_between"),
                ft.Row([ft.Text("نوع تسویه:"), ft.Text(last_sale['type'], weight="bold")]),
                ft.Divider(),
                ft.Row([ft.Text("مبلغ قابل پرداخت:", weight="bold"), ft.Text(f"{last_sale['price']:,} تومان", weight="bold", color="green900")], alignment="space_between")
            ], height=220, scroll="auto"),
            actions=[ft.ElevatedButton("بستن / چاپ", on_click=close_dialog)]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    tab_sales = ft.Column([
        sale_customer, sale_item, sale_qty, sale_price, sale_payment_type,
        ft.Row([
            ft.ElevatedButton("ثبت فروش", on_click=add_sale, style=ft.ButtonStyle(bgcolor="blue800", color="white")),
            ft.OutlinedButton("صدور و پرینت فاکتور", on_click=print_invoice_dialog)
        ], alignment="center"),
        ft.Divider(),
        ft.Text("لیست آخرین فروش‌ها:", weight="bold"),
        sales_list_ui
    ], horizontal_alignment="center")

    # ---------------------------------------------------------
    # بخش ۴: خرید کارگاه
    # ---------------------------------------------------------
    purchaser = ft.Dropdown(
        label="خریدار",
        width=310,
        options=[
            ft.dropdown.Option("محمد"),
            ft.dropdown.Option("حسین"),
            ft.dropdown.Option("متفرقه / کارگاه"),
        ],
        value="محمد"
    )
    purchase_item = ft.TextField(label="شرح خرید / قطعه / چوب", width=310, height=48)
    purchase_cost = ft.TextField(label="مبلغ خرید (تومان)", width=310, height=48, keyboard_type="number")
    purchase_date = ft.TextField(label="تاریخ خرید", value=datetime.now().strftime("%Y/%m/%d"), width=310, height=48)
    purchase_list_ui = ft.Column()

    def add_purchase(e):
        if purchase_item.value and purchase_cost.value:
            try:
                cost = int(purchase_cost.value.replace(",", ""))
                buyer = purchaser.value
                item = purchase_item.value
                date = purchase_date.value

                purchase_logs.append({"buyer": buyer, "item": item, "cost": cost, "date": date})

                purchase_list_ui.controls.insert(0,
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"{item} (خریدار: {buyer})", weight="bold"),
                                ft.Text(f"تاریخ: {date} | هزینه: {cost:,} تومان", size=11, color="red800")
                            ]),
                            ft.Icon(name="build", color="orange")
                        ], alignment="space_between"),
                        padding=8, bgcolor="orange50", border_radius=6
                    )
                )
                purchase_item.value = ""
                purchase_cost.value = ""
                update_analytics_ui()
                page.update()
            except ValueError:
                pass

    tab_purchase = ft.Column([
        purchaser, purchase_item, purchase_cost, purchase_date,
        ft.ElevatedButton("ثبت خرید کارگاه", on_click=add_purchase, style=ft.ButtonStyle(bgcolor="orange800", color="white")),
        ft.Divider(),
        ft.Text("خریدهای ثبت شده کارگاه:", weight="bold"),
        purchase_list_ui
    ], horizontal_alignment="center")

    # ---------------------------------------------------------
    # بخش ۵: نمودارها و گزارشات ماهانه
    # ---------------------------------------------------------
    analytics_ui = ft.Column()

    def update_analytics_ui():
        analytics_ui.controls.clear()
        
        total_sales = sum(s["price"] for s in sales_logs)
        total_purchases = sum(p["cost"] for p in purchase_logs)
        
        # آمار سازنده‌ها
        hussein_prod = sum(p["qty"] for p in production_logs if p["maker"] == "حسین")
        mohammad_prod = sum(p["qty"] for p in production_logs if p["maker"] == "محمد")
        cnc_prod = sum(p["qty"] for p in production_logs if p["maker"] == "CNC")

        analytics_ui.controls.extend([
            ft.Container(
                content=ft.Column([
                    ft.Text("خلاصه عملکرد مالی ماهانه", weight="bold", color="white"),
                    ft.Text(f"مجموع فروش: {total_sales:,} تومان", color="white"),
                    ft.Text(f"مجموع خرید کارگاه: {total_purchases:,} تومان", color="white"),
                    ft.Text(f"سود ناخالص: {total_sales - total_purchases:,} تومان", weight="bold", color="yellow")
                ]),
                padding=12, bgcolor="blueGrey800", border_radius=10, width=310
            ),
            ft.Divider(),
            ft.Text("گزارش سهم تولید استادکاران:", weight="bold"),
            ft.Text(f"🔨 تولید حسین: {hussein_prod} عدد"),
            ft.Text(f"🔨 تولید محمد: {mohammad_prod} عدد"),
            ft.Text(f"⚙️ تولید دستگاه CNC: {cnc_prod} عدد"),
        ])

    tab_analytics = ft.Column([
        ft.Text("گزارشات و تحلیل‌های ماهانه", size=16, weight="bold"),
        ft.Divider(),
        analytics_ui
    ], horizontal_alignment="center")

    # مقداردهی اولیه انبار و گزارشات
    update_inventory_ui()
    update_analytics_ui()

    # ---------------------------------------------------------
    # ایجاد تب‌های اصلی برنامه (استفاده از label به جای text)
    # ---------------------------------------------------------
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(label="تولید روزانه", icon="precision_manufacturing", content=tab_production),
            ft.Tab(label="انبار", icon="inventory", content=tab_inventory),
            ft.Tab(label="فروش", icon="shopping_cart", content=tab_sales),
            ft.Tab(label="خرید کارگاه", icon="build", content=tab_purchase),
            ft.Tab(label="گزارشات", icon="bar_chart", content=tab_analytics),
        ],
        expand=True
    )

    page.add(
        ft.Column([
            logo,
            ft.Text("صنایع چوب داتیس وود", size=18, weight="bold", color="green800"),
            ft.Divider()
        ], horizontal_alignment="center"),
        tabs
    )

ft.app(target=main)
