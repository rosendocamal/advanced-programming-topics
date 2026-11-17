import flet as ft
import inspect, random

CONST_WIDTH = 150
CONST_HEIGHT = 150

def opacity_animation(callback):
    def animate_opacity(e: ft.Event[ft.Button]):
        container.opacity = 0 if container.opacity == 1 else 1
        container.bgcolor = ft.Colors.WHITE_54 if random.randint(0, 1) else ft.Colors.BLACK_54
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


def sunflower_animation(callback):
    import logging
    import math
    import random
    from dataclasses import dataclass

    logging.basicConfig(level=logging.INFO)
    logging.getLogger("flet_components").setLevel(logging.INFO)

    MAX_SEEDS = 250
    DIALOG_WIDTH = 760
    DIALOG_HEIGHT = 620
    rng = random.Random()

    @dataclass
    class Seed:
        x: float
        y: float
        inner: bool = False

    def compute_seeds(count: int) -> list[Seed]:
        seeds = []
        tau = math.tau
        phi = (math.sqrt(5) + 1) / 2

        for i in range(count):
            theta = i * tau / phi
            radius = math.sqrt(i) / 40
            seeds.append(
                Seed(
                    x=radius * math.cos(theta),
                    y=-radius * math.sin(theta),
                    inner=True,
                )
            )

        for i in range(count, MAX_SEEDS):
            angle = tau * i / (MAX_SEEDS - 1)
            seeds.append(
                Seed(
                    x=math.cos(angle) * 0.9,
                    y=math.sin(angle) * 0.9,
                )
            )

        return seeds

    def make_seed_controls(
        seeds: list[Seed], animated: bool = True
    ) -> list[ft.Control]:
        return [
            ft.Container(
                width=5,
                height=5,
                bgcolor=ft.Colors.ORANGE if seed.inner else ft.Colors.GREY_700,
                align=ft.Alignment(seed.x, seed.y),
                animate_align=(
                    ft.Animation(round(rng.random() * 500) + 250)
                    if animated
                    else None
                ),
                border_radius=2.5,
            )
            for seed in seeds
        ]

    def open_sunflower(event: ft.Event[ft.Button]):
        page = event.control.page
        initial_count = MAX_SEEDS // 2
        seed_stack = ft.Stack(
            controls=make_seed_controls(compute_seeds(initial_count)),
            aspect_ratio=1.0,
        )
        seed_count_text = ft.Text(
            f"Showing {initial_count} seeds",
            text_align=ft.TextAlign.CENTER,
        )

        def update_seed_count(e: ft.Event[ft.Slider]):
            count = round(e.control.value)
            seed_stack.controls = make_seed_controls(compute_seeds(count))
            seed_count_text.value = (
                f"Showing {count} seed{'s' if count != 1 else ''}"
            )
            seed_stack.update()
            seed_count_text.update()

        def close_sunflower(e: ft.Event[ft.Button]):
            page.pop_dialog()
            callback(inspect.getsource(sunflower_animation))

        close_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            tooltip="Cerrar girasol",
            on_click=close_sunflower,
        )
        slider = ft.Slider(
            min=1,
            max=MAX_SEEDS,
            value=initial_count,
            width=300,
            on_change=update_seed_count,
        )
        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                alignment=ft.Alignment.CENTER,
                content_padding=0,
                content=ft.Container(
                    width=DIALOG_WIDTH,
                    height=DIALOG_HEIGHT,
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text("Sunflower", size=20, expand=True),
                                    close_button,
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Container(
                                content=seed_stack,
                                alignment=ft.Alignment.CENTER,
                                expand=True,
                            ),
                            ft.Row(
                                controls=[seed_count_text],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Row(
                                controls=[slider],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                    ),
                ),
            ),
        )
        callback(inspect.getsource(sunflower_animation))

    flower_preview = ft.Stack(
        width=CONST_WIDTH,
        height=CONST_HEIGHT,
        controls=make_seed_controls(
            compute_seeds(MAX_SEEDS // 2),
            animated=True,
        ),
    )
    button = ft.Button(
        content="¡Florece!",
        on_click=open_sunflower,
        align=ft.Alignment.CENTER,
    )

    return ft.SafeArea(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[flower_preview, button],
        ),
    )