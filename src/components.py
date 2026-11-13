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


def color_morph_animation(callback):
    def animate_morph(e: ft.Event[ft.Button]):
        is_circle = container.border_radius == CONST_WIDTH / 2
        container.border_radius = 10 if is_circle else CONST_WIDTH / 2
        container.bgcolor = ft.Colors.WHITE_54 if is_circle else ft.Colors.AMBER_400
        container.update()
        callback(inspect.getsource(color_morph_animation))

    return ft.SafeArea(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                container := ft.Container(
                    width=CONST_WIDTH,
                    height=CONST_HEIGHT,
                    bgcolor=ft.Colors.WHITE_54,
                    border_radius=10,
                    animate=ft.Animation(
                        duration=600,
                        curve=ft.AnimationCurve.EASE_IN_OUT,
                    ),
                ),
                ft.Button("¡Transfórmame!", on_click=animate_morph),
            ],
        ),
    )


def offset_slide_animation(callback):
    def animate_offset(e: ft.Event[ft.Button]):
        container.offset = (
            ft.Offset(0, 0)
            if container.offset == ft.Offset(0.25, -0.15)
            else ft.Offset(0.25, -0.15)
        )
        container.update()
        callback(inspect.getsource(offset_slide_animation))

    return ft.SafeArea(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                container := ft.Container(
                    width=CONST_WIDTH,
                    height=CONST_HEIGHT,
                    bgcolor=ft.Colors.CYAN_300,
                    border_radius=15,
                    offset=ft.Offset(0, 0),
                    animate_offset=ft.Animation(
                        duration=500,
                        curve=ft.AnimationCurve.ELASTIC_OUT,
                    ),
                ),
                ft.Button("¡Deslízame!", on_click=animate_offset),
            ],
        ),
    )


def flip_switcher_animation(callback):
    def animate_switch(e: ft.Event[ft.Button]):
        switcher.content = (
            icon_b if switcher.content == icon_a else icon_a
        )
        switcher.update()
        callback(inspect.getsource(flip_switcher_animation))

    icon_a = ft.Container(
        width=CONST_WIDTH,
        height=CONST_HEIGHT,
        bgcolor=ft.Colors.WHITE_54,
        border_radius=15,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.ROCKET_LAUNCH, size=60, color=ft.Colors.PINK_ACCENT),
    )

    icon_b = ft.Container(
        width=CONST_WIDTH,
        height=CONST_HEIGHT,
        bgcolor=ft.Colors.DEEP_PURPLE_400,
        border_radius=75,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.AUTO_AWESOME, size=60, color=ft.Colors.AMBER_300),
    )

    return ft.SafeArea(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                switcher := ft.AnimatedSwitcher(
                    content=icon_a,
                    transition=ft.AnimatedSwitcherTransition.SCALE,
                    duration=500,
                    reverse_duration=300,
                    switch_in_curve=ft.AnimationCurve.BOUNCE_OUT,
                ),
                ft.Button("¡Cámbiamelo!", on_click=animate_switch),
            ],
        ),
    )