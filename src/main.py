import flet as ft
import threading
import components as widget


class State:
    i = 0

s = State()
sem = threading.Semaphore()


def main(page: ft.Page):
    page.title = "Tópicos Avanzados de Programación"
    page.vertical_alignment = ft.MainAxisAlignment.SPACE_BETWEEN
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.theme_mode = ft.ThemeMode.DARK
    page.adaptive = True


    code_txt = ft.Text(
        value="Selecciona un botón para generar un evento.",
        color=ft.Colors.PINK_ACCENT,
        italic=True,
    )

    def show_code(code = str()):
        code_txt.value = code
        code_txt.update()

    def on_scroll(e: ft.OnScrollEvent):
        if e.pixels >= e.max_scroll_extent - 100 and sem.acquire(blocking=False):
            try:
                right_column.update()
            finally:
                sem.release()

    # Aquí es donde se agregarán las animaciones de components.py
    left_column_content = (widget.opacity_animation(show_code), widget.rotation_animation(show_code), widget.scale_animation(show_code))

    left_column = ft.GridView(
                            expand=True,
                            runs_count=3,
                            max_extent=250,
                            child_aspect_ratio=1.0,
                            spacing=3,
                            run_spacing=3,
                            controls=[
                                i for i in left_column_content
                            ]
                        )

    right_column = ft.Column(
                            width=800,
                            scroll=ft.ScrollMode.ALWAYS,
                            scroll_interval=0,
                            on_scroll=on_scroll,
                            controls=[code_txt]
                        )

    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Row(
                expand=True,
                controls=[
                    ft.Container(
                        width=800,
                        height=800,
                        expand=True,
                        margin=15,
                        padding=30,
                        bgcolor=ft.Colors.PINK_ACCENT,
                        border_radius=10,
                        content=left_column,
                        alignment=ft.Alignment.CENTER,
                    ), ft.Container(
                        width=800,
                        height=800,
                        expand=True,
                        margin=15,
                        padding=30,
                        bgcolor=ft.Colors.WHITE_10,
                        border_radius=10,
                        content=right_column,
                        alignment=ft.Alignment.TOP_LEFT,
                    ),
                ]
            )
        )
    )


if __name__ == "__main__":
    ft.run(main)