import flet as ft
import threading, tkinter
import components as widget


class State:
    i = 0

s = State()
sem = threading.Semaphore()

tk = tkinter.Tk()
SCREEN_WIDTH = tk.winfo_screenwidth()
SCREEN_HEIGHT = tk.winfo_screenheight()
SCREEN_800 = int(SCREEN_WIDTH / 2.4)

def main(page: ft.Page):
    page.title = "Tópicos Avanzados de Programación"
    page.vertical_alignment = ft.MainAxisAlignment.SPACE_BETWEEN
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.theme_mode = ft.ThemeMode.DARK
    page.adaptive = False
    page.window.resizable = True
    page.window.width = SCREEN_WIDTH
    page.window.height = SCREEN_HEIGHT
    page.window.focused = False
    page.window.prevent_close = False
    page.window.full_screen = False


    code_txt_value = "Selecciona un botón para generar un evento."
    code_txt = ft.Text(
        value=code_txt_value,
        color=ft.Colors.PINK_ACCENT,
        italic=True,
    )

    def show_code(code = str()):
        code_txt.value = code
        code_txt.update()

    def clean_code():
        code_txt.value = code_txt_value
        code_txt.update()

    async def close_app():
        await page.window.destroy()

    def full_screen_app():
        page.window.full_screen = True
        button_full_screen_app.icon = ft.Icons.FULLSCREEN_EXIT
        button_full_screen_app.on_click = full_screen_exit_app

    def full_screen_exit_app():
        page.window.full_screen = False
        button_full_screen_app.icon = ft.Icons.FULLSCREEN
        button_full_screen_app.on_click = full_screen_app

    def on_scroll(e: ft.OnScrollEvent):
        if e.pixels >= e.max_scroll_extent - 100 and sem.acquire(blocking=False):
            try:
                right_column.update()
            finally:
                sem.release()

    # Aquí es donde se agregarán las animaciones de components.py
    left_column_content = (
        widget.opacity_animation(show_code),
        widget.rotation_animation(show_code),
        widget.scale_animation(show_code),
        widget.color_morph_animation(show_code),
        widget.offset_slide_animation(show_code),
        widget.flip_switcher_animation(show_code),
        widget.sunflower_animation(show_code),
        widget.timer_animation(show_code),
        widget.rubik_cube_component(show_code),
        widget.heart_animation(show_code),
        widget.phone_animation(show_code),
        widget.ball_animation(show_code),
    )

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
                            width=SCREEN_800,
                            scroll=ft.ScrollMode.ALWAYS,
                            scroll_interval=0,
                            on_scroll=on_scroll,
                            controls=[code_txt]
                        )

    button_full_screen_app = ft.IconButton(hover_color=ft.Colors.PINK_ACCENT, icon=ft.Icons.FULLSCREEN, icon_color=ft.Colors.WHITE, on_click=full_screen_app)

    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Row(
                expand=True,
                controls=[
                    ft.Container(
                        width=SCREEN_800,
                        height=SCREEN_800,
                        expand=True,
                        margin=15,
                        padding=30,
                        bgcolor=ft.Colors.PINK_ACCENT,
                        border_radius=20,
                        content=left_column,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(
                        width=SCREEN_800,
                        height=SCREEN_800,
                        expand=True,
                        margin=15,
                        padding=30,
                        bgcolor=ft.Colors.WHITE_10,
                        border_radius=20,
                        content=right_column,
                        alignment=ft.Alignment.TOP_LEFT,
                    ),
                ]
            )
        ),
        ft.BottomAppBar(
            margin=15,
            border_radius=ft.BorderRadius.all(20),
            bgcolor=ft.Colors.PINK_ACCENT_100,
            content=ft.Row(
                controls=[
                    ft.Container(expand=True),
                    ft.IconButton(hover_color=ft.Colors.PINK_ACCENT, icon=ft.Icons.CLEAR_ROUNDED, icon_color=ft.Colors.WHITE, on_click=clean_code),
                    button_full_screen_app,
                    ft.IconButton(hover_color=ft.Colors.PINK_ACCENT, icon=ft.Icons.EXIT_TO_APP, icon_color=ft.Colors.WHITE, on_click=close_app, on_long_press=close_app),
                ]
            ),
        )
    )


if __name__ == "__main__":
    ft.run(main)