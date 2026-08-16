import flet as ft

def main(page: ft.Page):
    page.title = "داتیس وود - مدیریت کامل کارگاه"
    page.theme_mode = "light"
    page.rtl = True
    page.scroll = "auto"
    page.padding = 10

    # لوگو
    logo = ft.Image(src="assets/logo.png", width=120, height=70, fit="contain")

    # ---------------------------------------------------------
    # تب ۱: فاکتور فروش
    # ---------------------------------------------------------
    customer_name = ft.TextField(label="نام مشتری", width=300, height=45)
    item_name = ft.TextField(label="نام کالا / محصول", width=300, height=45)
    item_price = ft.TextField(label="قیمت (تومان)", width=300, height=45, keyboard_type="number")
    
    invoice_items = []
    invoice_list_ui = ft.Column()
    total_invoice_text = ft.Text("جمع کل: ۰ تومان", size=15, weight="bold", color="green800")

    def update_invoice_ui():
        invoice_list_ui.controls.clear()
        total = 0
        for idx, item in enumerate(invoice_items):
            total += item["price"]
            invoice_list_ui.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"{idx+1}. {item['name']}"),
                        ft.Text(f"{item['price']:,} تومان")
                    ], alignment="space_between"),
                    padding=8, bgcolor="grey100", border_radius=6
                )
            )
        total_invoice_text.value = f"جمع کل: {total:,} تومان"
        page.update()

    def add_invoice_item(e):
        if item_name.value and item_price.value:
            try:
                p = int(item_price.value.replace(",", ""))
                invoice_items.append({"name": item_name.value, "price": p})
                item_name.value = ""
                item_price.value = ""
                update_invoice_ui()
            except ValueError:
                pass

    def show_preview(e):
        if not invoice_items:
            return
        
        def close_dialog(e):
            dialog.open = False
            page.update()

        total = sum(i["price"] for i in invoice_items)
        rows = [ft.Row([ft.Text("کالا", weight="bold"), ft.Text("مبلغ", weight="bold")], alignment="space_between"), ft.Divider()]
        for idx, item in enumerate(invoice_items):
            rows.append(ft.Row([ft.Text(item['name']), ft.Text(f"{item['price']:,}")], alignment="space_between"))

        dialog = ft.AlertDialog(
            title=ft.Text("پیش‌نمایش فاکتور داتیس وود", size=16, weight="bold"),
            content=ft.Column(rows + [ft.Divider(), ft.Text(f"جمع: {total:,} تومان", weight="bold", color="green800")], scroll="auto", height=200),
            actions=[ft.ElevatedButton("بستن", on_click=close_dialog)]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    tab_invoice = ft.Column([
        customer_name, item_name, item_price,
        ft.Row([
            ft.ElevatedButton("افزودن کالا", on_click=add_invoice_item, style=ft.ButtonStyle(bgcolor="green", color="white")),
            ft.OutlinedButton("فاکتور جدید", on_click=lambda e: (invoice_items.clear(), update_invoice_ui()))
        ], alignment="center"),
        ft.Divider(),
        invoice_list_ui,
        total_invoice_text,
        ft.ElevatedButton("پیش‌نمایش فاکتور", on_click=show_preview, style=ft.ButtonStyle(bgcolor="blue", color="white"))
    ], horizontal_alignment="center")

    # ---------------------------------------------------------
    # تب ۲: ورودی و تولید روزانه
    # ---------------------------------------------------------
    daily_title = ft.TextField(label="شرح فعالیت / تولید روزانه", width=300, height=45)
    daily_qty = ft.TextField(label="تعداد / مقدار", width=300, height=45, keyboard_type="number")
    daily_list_ui = ft.Column()

    def add_daily_entry(e):
        if daily_title.value:
            q = daily_qty.value or "۱"
            daily_list_ui.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(daily_title.value, weight="bold"),
                        ft.Text(f"تعداد: {q}")
                    ], alignment="space_between"),
                    padding=8, bgcolor="blue50", border_radius=6
                )
            )
            daily_title.value = ""
            daily_qty.value = ""
            page.update()

    tab_daily = ft.Column([
        daily_title, daily_qty,
        ft.ElevatedButton("ثبت ورودی روزانه", on_click=add_daily_entry, style=ft.ButtonStyle(bgcolor="blue", color="white")),
        ft.Divider(),
        ft.Text("گزارش تولیدات امروز:", weight="bold"),
        daily_list_ui
    ], horizontal_alignment="center")

    # ---------------------------------------------------------
    # تب ۳: انبار و خریدهای کارگاه
    # ---------------------------------------------------------
    purchase_item = ft.TextField(label="نام قطعه / چوب / ابزار", width=300, height=45)
    purchase_cost = ft.TextField(label="هزینه خرید (تومان)", width=300, height=45, keyboard_type="number")
    inventory_list_ui = ft.Column()

    def add_purchase(e):
        if purchase_item.value and purchase_cost.value:
            try:
                c = int(purchase_cost.value.replace(",", ""))
                inventory_list_ui.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(purchase_item.value, weight="bold"),
                            ft.Text(f"{c:,} تومان", color="red700")
                        ], alignment="space_between"),
                        padding=8, bgcolor="amber50", border_radius=6
                    )
                )
                purchase_item.value = ""
                purchase_cost.value = ""
                page.update()
            except ValueError:
                pass

    tab_inventory = ft.Column([
        purchase_item, purchase_cost,
        ft.ElevatedButton("ثبت خرید کارگاه", on_click=add_purchase, style=ft.ButtonStyle(bgcolor="orange", color="white")),
        ft.Divider(),
        ft.Text("خریدهای ثبت شده کارگاه:", weight="bold"),
        inventory_list_ui
    ], horizontal_alignment="center")

    # ---------------------------------------------------------
    # ساختن تب‌ها و چیدمان نهایی
    # ---------------------------------------------------------
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="فاکتور فروش", icon="receipt", content=tab_invoice),
            ft.Tab(text="ورودی روزانه", icon="today", content=tab_daily),
            ft.Tab(text="انبار و خریدها", icon="inventory", content=tab_inventory),
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
