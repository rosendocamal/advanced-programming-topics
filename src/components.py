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
    from dataclasses import dataclass, field
    from typing import cast

    logging.basicConfig(level=logging.INFO)
    logging.getLogger("flet_components").setLevel(logging.INFO)

    MAX_SEEDS = 250
    rng = random.Random()

    @dataclass
    class Seed:
        key: int
        x: float
        y: float
        inner: bool = False

    @dataclass
    class AppModel(ft.Observable):
        seeds_count: float = MAX_SEEDS // 2
        seeds: list[Seed] = field(default_factory=list)

        def __post_init__(self):
            ft.context.page.title = "Sunflower"
            self.rebuild_seeds()

        def update_seeds_count(self, new_seeds_count: float):
            self.seeds_count = new_seeds_count
            self.rebuild_seeds()

        def rebuild_seeds(self):
            count = round(self.seeds_count)
            self.seeds.clear()
            tau = math.tau
            phi = (math.sqrt(5) + 1) / 2

            for i in range(count):
                theta = i * tau / phi
                radius = math.sqrt(i) / 40
                self.seeds.append(
                    Seed(
                        key=i,
                        x=radius * math.cos(theta),
                        y=-radius * math.sin(theta),
                        inner=True,
                    )
                )

            for j in range(count, MAX_SEEDS):
                angle = tau * j / (MAX_SEEDS - 1)
                self.seeds.append(
                    Seed(
                        key=j,
                        x=math.cos(angle) * 0.9,
                        y=math.sin(angle) * 0.9,
                    )
                )

    @ft.component
    def SeedView(seed: Seed, key=None) -> ft.Control:
        return ft.Container(
            width=5,
            height=5,
            bgcolor=ft.Colors.ORANGE if seed.inner else ft.Colors.GREY_700,
            align=ft.Alignment(seed.x, seed.y),
            animate_align=ft.Animation(round(rng.random() * 500) + 250),
            border_radius=2.5,
        )

    @ft.component
    def Sunflower():
        model, _ = ft.use_state(lambda: AppModel())
        memoized_seed_view = ft.memo(SeedView)

        return ft.View(
            appbar=ft.AppBar(title=ft.Text("Sunflower")),
            controls=[
                ft.SafeArea(
                    expand=True,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                        controls=[
                            ft.Container(
                                content=ft.Stack(
                                    controls=[
                                        memoized_seed_view(seed, key=seed.key)
                                        for seed in model.seeds
                                    ],
                                    aspect_ratio=1.0,
                                ),
                                alignment=ft.Alignment.CENTER,
                                expand=True,
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        f"Showing {round(model.seeds_count)} "
                                        f"seed{'s' if model.seeds_count != 1 else ''}"
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Row(
                                [
                                    ft.Slider(
                                        min=1,
                                        max=MAX_SEEDS,
                                        value=model.seeds_count,
                                        width=300,
                                        on_change=lambda e: model.update_seeds_count(
                                            cast(float, e.control.value)
                                        ),
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                    ),
                )
            ],
        )

    def open_sunflower(_event: ft.Event[ft.Button]):
        ft.run(lambda page: page.render_views(Sunflower))
        callback(inspect.getsource(sunflower_animation))

    return ft.SafeArea(
        content=ft.Column(
            controls=[
                ft.Container(
                    width=CONST_WIDTH,
                    height=CONST_HEIGHT,
                    bgcolor=ft.Colors.WHITE_54,
                    border_radius=10,
                    animate_opacity=600,
                    align=ft.Alignment.CENTER,
                ),
                ft.Button(
                    content="¡Tocáme!",
                    on_click=open_sunflower,
                    align=ft.Alignment.CENTER,
                ),
            ],
        ),
    )