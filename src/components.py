import flet as ft


class BotonQueDesaparece(ft.Container):

    def __init__(self, codigo_fuente: str):
        super().__init__(self)
        self.codigo_fuente = codigo_fuente

        # Definimos el botón inicial dentro del componente
        self.boton = ft.Button(
            content="Mostrar código fuente",
            icon=ft.Icons.CODE,
            bgcolor=ft.Colors.BLUE_GREY_800,
            color=ft.Colors.WHITE,
            on_click=self.revelar_codigo,
        )

        # El contenedor arranca mostrando el botón
        self.content = self.boton
        self.padding = 10

    def revelar_codigo(self, e):
        # Al hacer clic, reemplazamos el contenido del contenedor
        # El botón desaparece y se dibuja un bloque de texto con el código
        self.content = ft.Container(
            content=ft.Text(
                self.codigo_fuente,
                font_family="monospace",
                color=ft.Colors.GREEN_ACCENT_400,
            ),
            bgcolor=ft.Colors.BLACK_87,
            padding=15,
            border_radius=8,
        )
        # Actualizamos el componente para que refleje el cambio en la interfaz
        self.update()