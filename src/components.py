from rubik_view import open_rubik_interface
import random
import flet as ft
import inspect

CONST_WIDTH = 150
CONST_HEIGHT = 150

def opacity_animation(callback):
    def animate_opacity(e: ft.Event[ft.Button]):
        container.opacity = 0 if container.opacity == 1 else 1
        container.update()
        callback(inspect.getsource(opacity_animation))

    return ft.SafeArea(
            content=ft.Column(
                controls=[
                    container := ft.Container(
                        width=CONST_WIDTH,
                        height=CONST_HEIGHT,
                        bgcolor=ft.Colors.WHITE_54,
                        border_radius=10,
                        animate_opacity=600,
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

def rotation_animation(callback):
    from math import pi

    def animate_rotation(e: ft.Event[ft.Button]):
        container.rotate.angle += pi / 2
        container.update()
        callback(inspect.getsource(rotation_animation))

    return ft.SafeArea(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    container := ft.Container(
                        width=CONST_WIDTH,
                        height=CONST_HEIGHT,
                        bgcolor=ft.Colors.WHITE_54,
                        border_radius=5,
                        rotate=ft.Rotate(angle=0, alignment=ft.Alignment.CENTER),
                        animate_rotation=ft.Animation(
                            duration=600,
                            curve=ft.AnimationCurve.DECELERATE,
                        ),
                    ),
                    ft.Button("¡Presióname!", on_click=animate_rotation),
                ],
            ),
        )

def scale_animation(callback):
    from math import pi

    def animate_rotation(e: ft.Event[ft.Button]):
        container.scale = 1 if container.scale == 0.5 else 0.5
        container.update()
        callback(inspect.getsource(scale_animation))

    return ft.SafeArea(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    container := ft.Container(
                        width=CONST_WIDTH,
                        height=CONST_HEIGHT,
                        bgcolor=ft.Colors.WHITE_54,
                        border_radius=5,
                        scale=1,
                        animate_scale=ft.Animation(
                            duration=600,
                            curve=ft.AnimationCurve.BOUNCE_OUT,
                        ),
                    ),
                    ft.Button("¡Hazme tuyo!", on_click=animate_rotation),
                ],
            ),
        )

def rubik_cube_component(callback):
    palette = [
        ft.Colors.RED_500,
        ft.Colors.GREEN_500,
        ft.Colors.BLUE_500,
        ft.Colors.YELLOW_400,
        ft.Colors.ORANGE_500,
        ft.Colors.WHITE,
    ]

    mini_grid = ft.GridView(
        runs_count=3,
        width=CONST_WIDTH,
        height=CONST_HEIGHT,
        spacing=3,
        run_spacing=3,
        controls=[
            ft.Container(
                bgcolor=random.choice(palette),
                border_radius=4,
                animate=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
            )
            for _ in range(9)
        ],
    )

    def shuffle_preview(e):
        for cell in mini_grid.controls:
            cell.bgcolor = random.choice(palette)
        mini_grid.update()
        callback(inspect.getsource(rubik_cube_component))

    def enter_rubik_ui(e: ft.Event[ft.Button]):
        callback(inspect.getsource(rubik_cube_component))
        open_rubik_interface(e.page)

    return ft.SafeArea(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.GestureDetector(
                    on_tap=shuffle_preview,
                    on_pan_update=shuffle_preview,
                    content=mini_grid,
                ),
                ft.Button("Resolver Cubo", on_click=enter_rubik_ui),
            ],
        ),
    )