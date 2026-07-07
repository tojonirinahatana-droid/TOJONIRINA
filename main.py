import flet as ft

def main(page: ft.Page):
    page.title = "TOJONIRINA App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    page.add(
        ft.Row(
            [
                ft.Text("Miarahaba anao,", size=30),
                ft.Text("TOJONIRINA!", size=30, weight="bold", color="blue"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

ft.app(target=main)