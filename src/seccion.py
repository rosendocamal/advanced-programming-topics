import flet as ft


def main(page: ft.Page):
    page.title = "Simulador Launcher - OS"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#121212"
    page.padding = 0

    # Historial de navegación para el botón de retroceso (Triángulo)
    historial_vistas = []

    # Contenedor central donde cambian las vistas
    contenido_principal = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
    )

    def actualizar_pantalla(nuevo_contenido, guardar_historial=True):
        if guardar_historial and len(contenido_principal.controls) > 0:
            historial_vistas.append(list(contenido_principal.controls))
        contenido_principal.controls = [nuevo_contenido]
        page.update()

    # --- PANTALLA PRINCIPAL (HOME) ---
    def mostrar_home(e=None):
        # Barra de búsqueda superior
        barra_busqueda = ft.TextField(
            hint_text="Buscar aplicación...",
            prefix_icon=ft.Icons.SEARCH,
            border_color="#444444",
            focused_border_color="#FFFFFF",
            color="#FFFFFF",
            bgcolor="#1E1E1E",
            border_radius=8,
            width=320,
            height=45,
        )

        # Acciones para abrir las Apps
        def abrir_app_1(e):
            vista_app1 = ft.Column(
                [
                    ft.Text(
                        "Interfaz de App 1",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#FFFFFF",
                    ),
                    ft.Text(
                        "Bienvenido a la aplicación número uno.",
                        color="#AAAAAA",
                    ),
                    ft.Button(
                        content="Acción en App 1",
                        color="#000000",
                        bgcolor="#FFFFFF",
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
            )
            actualizar_pantalla(vista_app1)

        def abrir_app_2(e):
            vista_app2 = ft.Column(
                [
                    ft.Text(
                        "Interfaz de App 2",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#FFFFFF",
                    ),
                    ft.Text(
                        "Panel de control de la aplicación dos.",
                        color="#AAAAAA",
                    ),
                    ft.Button(
                        content="Acción en App 2",
                        color="#000000",
                        bgcolor="#FFFFFF",
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
            )
            actualizar_pantalla(vista_app2)

        # Tarjetas de aplicaciones abajo (con ft.Border.all en mayúscula)
        btn_app1 = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "App 1", color="#FFFFFF", weight=ft.FontWeight.BOLD
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#1E1E1E",
            width=140,
            height=100,
            border_radius=12,
            border=ft.Border.all(1, "#444444"),
            ink=True,
            on_click=abrir_app_1,
        )

        btn_app2 = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "App 2", color="#FFFFFF", weight=ft.FontWeight.BOLD
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#1E1E1E",
            width=140,
            height=100,
            border_radius=12,
            border=ft.Border.all(1, "#444444"),
            ink=True,
            on_click=abrir_app_2,
        )

        fila_apps = ft.Row(
            [btn_app1, btn_app2],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        home_layout = ft.Column(
            [
                barra_busqueda,
                ft.Container(height=10),
                fila_apps,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        historial_vistas.clear()
        actualizar_pantalla(home_layout, guardar_historial=False)

    # --- BOTONES DE NAVEGACIÓN INFERIOR (Estilo Xiaomi) ---
    def accion_cuadrado(e):
        pass

    def accion_circulo(e):
        mostrar_home()

    def accion_triangulo(e):
        if historial_vistas:
            anterior = historial_vistas.pop()
            contenido_principal.controls = anterior
            page.update()
        else:
            mostrar_home()

    nav_cuadrado = ft.IconButton(
        icon=ft.Icons.SQUARE_OUTLINED,
        icon_color="#AAAAAA",
        icon_size=18,
        on_click=accion_cuadrado,
        tooltip="Apps recientes",
    )

    nav_circulo = ft.IconButton(
        icon=ft.Icons.CIRCLE_OUTLINED,
        icon_color="#AAAAAA",
        icon_size=16,
        on_click=accion_circulo,
        tooltip="Inicio",
    )

    nav_triangulo = ft.IconButton(
        icon=ft.Icons.CHANGE_HISTORY,
        icon_color="#AAAAAA",
        icon_size=18,
        on_click=accion_triangulo,
        tooltip="Atrás",
    )

    barra_navegacion = ft.Container(
        content=ft.Row(
            [nav_cuadrado, nav_circulo, nav_triangulo],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        ),
        bgcolor="#1A1A1A",
        height=50,
        width=360,
    )

    # Inicializar vista de inicio
    mostrar_home()

    # Ensamblaje final de la página
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Column(
                [
                    ft.Container(
                        content=contenido_principal,
                        expand=True,
                    ),
                    barra_navegacion,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
    )


if __name__ == "__main__":
    ft.run(main)