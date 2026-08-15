import flet as ft

def main(page: ft.Page):
    # تنظیمات صفحه اصلی
    page.title = "داتیس وود - مدیریت فاکتور"
    page.theme_mode = "light"
    page.rtl = True
    page.scroll = "auto"
    page.padding = 15

    # ۱. لوگو و سربرگ اصلی - آدرس اصلاح شد
    logo = ft.Image(
        src="assets/logo.jpg", 
        width=160,
        height=90,
        fit="contain"
    )

    header = ft.Column(
        controls=[
            logo,
            ft.Text("صنایع چوب داتیس وود", size=20, weight="bold", color="green800"),
            ft.Text("سیستم صدور و ثبت فاکتور فروش", size=13, color="grey700"),
            ft.Divider()
        ],
        horizontal_alignment="center"
    )

    # ۲. ورودی‌های اطلاعات فاکتور
    customer_name = ft.TextField(label="نام مشتری", width=320, height=48)
    item_name = ft.TextField(label="نام کالا / محصول", width=320, height=48)
    item_price = ft.TextField(label="قیمت (تومان)", width=320, height=48, keyboard_type="number")

    # لیست نگهدارنده داده‌ها
    items_list = []
    invoice_items_ui = ft.Column()
    total_price_text = ft.Text("جمع کل: ۰ تومان", size=16, weight="bold", color="green900")

    # تابع به‌روزرسانی نمایش لیست و جمع کل
    def update_invoice_ui():
        invoice_items_ui.controls.clear()
        total = 0
        for idx, item in enumerate(items_list):
            total += item["price"]
            invoice_items_ui.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(f"{idx + 1}. {item['name']}", weight="bold"),
                            ft.Text(f"{item['price']:,} تومان"),
                        ],
                        alignment="space_between"
                    ),
                    padding=10,
                    bgcolor="grey100",
                    border_radius=8
                )
            )
        total_price_text.value = f"جمع کل: {total:,} تومان"
        page.update()

    # تابع افزودن آیتم
    def add_item_click(e):
        if item_name.value and item_price.value:
            try:
                price = int(item_price.value.replace(",", ""))
                items_list.append({"name": item_name.value, "price": price})
                item_name.value = ""
                item_price.value = ""
                update_invoice_ui()
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("لطفاً قیمت را به عدد وارد کنید"))
                page.snack_bar.open = True
                page.update()

    # تابع پاک کردن فاکتور
    def clear_invoice(e):
        items_list.clear()
        customer_name.value = ""
        update_invoice_ui()

    # تابع نمایش پنجره فاکتور نهایی جهت پرینت / ذخیره
    def show_print_preview(e):
        if not items_list:
            page.snack_bar = ft.SnackBar(ft.Text("هیچ کالا یا آیتمی اضافه نشده است!"))
            page.snack_bar.open = True
            page.update()
            return

        total = sum(i["price"] for i in items_list)
        preview_rows = [
            ft.Row([ft.Text("کالا", weight="bold"), ft.Text("مبلغ (تومان)", weight="bold")], alignment="space_between"),
            ft.Divider()
        ]
        for idx, item in enumerate(items_list):
            preview_rows.append(
                ft.Row([ft.Text(f"{idx+1}. {item['name']}"), ft.Text(f"{item['price']:,}")], alignment="space_between")
            )

        dialog = ft.AlertDialog(
            title=ft.Column([
                ft.Image(src="assets/logo.jpg", width=120, fit="contain"), # آدرس اصلاح شد
                ft.Text("فاکتور فروش داتیس وود", size=16, weight="bold"),
                ft.Text(f"مشتری: {customer_name.value or 'آزاد'}", size=13),
                ft.Divider()
            ], horizontal_alignment="center"),
            content=ft.Column(
                controls=preview_rows + [
                    ft.Divider(),
                    ft.Row([ft.Text("مبلغ قابل پرداخت:", weight="bold"), ft.Text(f"{total:,} تومان", weight="bold", color="green800")], alignment="space_between")
                ],
                scroll="auto",
                height=250
            ),
            actions=[
                ft.ElevatedButton("بستن", on_click=lambda _: page.close(dialog))
            ]
        )
        page.open(dialog)

    # دکمه‌ها
    add_button = ft.ElevatedButton(
        text="افزودن به فاکتور",
        icon="add",
        on_click=add_item_click,
        style=ft.ButtonStyle(color="white", bgcolor="green")
    )

    print_button = ft.ElevatedButton(
        text="پیش‌نمایش و چاپ فاکتور",
        icon="print",
        on_click=show_print_preview,
        style=ft.ButtonStyle(color="white", bgcolor="blue")
    )

    clear_button = ft.OutlinedButton(
        text="فاکتور جدید",
        icon="delete",
        on_click=clear_invoice
    )

    # چیدمان نهایی صفحه
    page.add(
        header,
        ft.Column(
            controls=[
                customer_name,
                item_name,
                item_price,
                ft.Row([add_button, clear_button], alignment="center"),
                ft.Divider(),
                ft.Text("آیتم‌های فاکتور فعلی:", weight="bold", size=15),
                invoice_items_ui,
                ft.Container(content=total_price_text, padding=10),
                print_button
            ],
            horizontal_alignment="center"
        )
    )

ft.app(target=main)
