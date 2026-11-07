# import flet as ft


# def main(page: ft.Page):
#     counter = ft.Text("0", size=50, data=0)

#     def increment_click(e: ft.Event[ft.FloatingActionButton]):
#         counter.data += 1
#         counter.value = str(counter.data)

#     page.floating_action_button = ft.FloatingActionButton(
#         icon=ft.Icons.ADD, key="increment", on_click=increment_click
#     )
#     page.add(
#         ft.SafeArea(
#             expand=True,
#             content=ft.Container(
#                 content=counter,
#                 alignment=ft.Alignment.CENTER,
#             ),
#         )
#     )


# if __name__ == "__main__":
#     ft.run(main)


import flet as ft
from componentes import BotonConSnippet


def main(page: ft.Page):
    page.title = "Botón que se convierte en código"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # El código fuente que quieres mostrar al presionar el botón
    snippet_ejemplo = """
      ft.ElevatedButton(
          text="Haz clic",
          on_click=lambda e: print("Acción ejecutada")
      )
      """
    
    # Instanciamos nuestro componente modularizado
    mi_componente = BotonConSnippet(snippet_ejemplo)
    
    page.add(mi_componente)


if __name__ == "__main__":
    ft.run(main)