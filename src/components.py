import flet as ft

def opacity_animation():
    def animate_opacity(e: ft.Event[ft.Button]):
        container.opacity = 0 if container.opacity == 1 else 1
        container.update()    

    return ft.SafeArea(
            content=ft.Column(
                controls=[
                    container := ft.Container(
                        width=150,
                        height=150,
                        bgcolor=ft.Colors.BLUE,
                        border_radius=10,
                        animate_opacity=300,
                        align=ft.Alignment.CENTER
                    ),
                    ft.Button(
                        content="¡Tocáme!",
                        on_click=animate_opacity,
                        align=ft.Alignment.CENTER
                    ),
                ],
            ),
        )

code_opacity_animation = """
def opacity_animation():
    def animate_opacity(e: ft.Event[ft.Button]):
        container.opacity = 0 if container.opacity == 1 else 1
        container.update()

    return ft.SafeArea(
            content=ft.Column(
                controls=[
                    container := ft.Container(
                        width=150,
                        height=150,
                        bgcolor=ft.Colors.BLUE,
                        border_radius=10,
                        animate_opacity=300,
                        align=ft.Alignment.CENTER
                    ),
                    ft.Button(
                        content="¡Tocáme!",
                        on_click=animate_opacity,
                        align=ft.Alignment.CENTER
                    ),
                ],
            ),
        )"""