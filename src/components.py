import flet as ft
import inspect, math, random, time, logging, asyncio, os, datetime
from dataclasses import dataclass
from rubik_view import open_rubik_interface
from main import SCREEN_WIDTH


COMPONENT_SIZE = int(SCREEN_WIDTH / 12.8)
DEFAULT_ANIMATION_DURATION_MS = 600

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
                        width=COMPONENT_SIZE,
                        height=COMPONENT_SIZE,
                        bgcolor=ft.Colors.WHITE_54,
                        border_radius=10,
                        animate_opacity=DEFAULT_ANIMATION_DURATION_MS,
                        align=ft.Alignment.CENTER
                    ),
                    ft.Button(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.PINK_ACCENT_400,
                        content="¡Tocáme!",
                        on_click=animate_opacity,
                        align=ft.Alignment.CENTER
                    ),
                ],
            ),
        )

def rotation_animation(callback):
    def animate_rotation(e: ft.Event[ft.Button]):
        container.rotate.angle += math.pi / 2
        container.update()
        callback(inspect.getsource(rotation_animation))

    return ft.SafeArea(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    container := ft.Container(
                        width=COMPONENT_SIZE,
                        height=COMPONENT_SIZE,
                        bgcolor=ft.Colors.WHITE_54,
                        border_radius=5,
                        rotate=ft.Rotate(
                            angle=0, 
                            alignment=ft.Alignment.CENTER
                        ),
                        animate_rotation=ft.Animation(
                            duration=DEFAULT_ANIMATION_DURATION_MS,
                            curve=ft.AnimationCurve.DECELERATE,
                        ),
                    ),
                    ft.Button(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.PINK_ACCENT_400,
                        content="¡Presióname!",
                        on_click=animate_rotation
                    ),
                ],
            ),
        )

def scale_animation(callback):
    def animate_rotation(e: ft.Event[ft.Button]):
        container.scale = 1 if container.scale == 0.5 else 0.5
        container.update()
        callback(inspect.getsource(scale_animation))

    return ft.SafeArea(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    container := ft.Container(
                        width=COMPONENT_SIZE,
                        height=COMPONENT_SIZE,
                        bgcolor=ft.Colors.WHITE_54,
                        border_radius=5,
                        scale=1,
                        animate_scale=ft.Animation(
                            duration=DEFAULT_ANIMATION_DURATION_MS,
                            curve=ft.AnimationCurve.BOUNCE_OUT,
                        ),
                    ),
                    ft.Button(
                        bgcolor=ft.Colors.PINK_ACCENT_400,
                        content="¡Hazme tuyo!", 
                        on_click=animate_rotation
                    ),
                ],
            ),
        )

def color_morph_animation(callback):
    def animate_morph(e: ft.Event[ft.Button]):
        is_circle = container.border_radius == COMPONENT_SIZE / 2
        container.border_radius = 10 if is_circle else COMPONENT_SIZE / 2
        container.bgcolor = ft.Colors.WHITE_54 if is_circle else ft.Colors.AMBER_400
        container.update()
        callback(inspect.getsource(color_morph_animation))

    return ft.SafeArea(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                container := ft.Container(
                    width=COMPONENT_SIZE,
                    height=COMPONENT_SIZE,
                    bgcolor=ft.Colors.WHITE_54,
                    border_radius=10,
                    animate=ft.Animation(
                        duration=DEFAULT_ANIMATION_DURATION_MS,
                        curve=ft.AnimationCurve.EASE_IN_OUT,
                    ),
                ),
                ft.Button(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.PINK_ACCENT_400,
                    content="¡Transfórmame!",
                    on_click=animate_morph
                ),
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
                    width=COMPONENT_SIZE,
                    height=COMPONENT_SIZE,
                    bgcolor=ft.Colors.CYAN_300,
                    border_radius=15,
                    offset=ft.Offset(0, 0),
                    animate_offset=ft.Animation(
                        duration=DEFAULT_ANIMATION_DURATION_MS,
                        curve=ft.AnimationCurve.ELASTIC_OUT,
                    ),
                ),
                ft.Button(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.PINK_ACCENT_400,
                    content="¡Deslízame!",
                    on_click=animate_offset
                ),
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
        width=COMPONENT_SIZE,
        height=COMPONENT_SIZE,
        bgcolor=ft.Colors.WHITE_54,
        border_radius=15,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(
            ft.Icons.ROCKET_LAUNCH,
            size=60,
            color=ft.Colors.PINK_ACCENT
        ),
    )

    icon_b = ft.Container(
        width=COMPONENT_SIZE,
        height=COMPONENT_SIZE,
        bgcolor=ft.Colors.DEEP_PURPLE_400,
        border_radius=75,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(
            ft.Icons.AUTO_AWESOME,
            size=60,
            color=ft.Colors.AMBER_300
        ),
    )

    return ft.SafeArea(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                switcher := ft.AnimatedSwitcher(
                    content=icon_a,
                    transition=ft.AnimatedSwitcherTransition.SCALE,
                    duration=DEFAULT_ANIMATION_DURATION_MS,
                    reverse_duration=DEFAULT_ANIMATION_DURATION_MS,
                    switch_in_curve=ft.AnimationCurve.BOUNCE_OUT,
                ),
                ft.Button(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.PINK_ACCENT_400,
                    content="¡Cámbiamelo!",
                    on_click=animate_switch),
            ],
        ),
    )

def sunflower_animation(callback):
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
                                    ft.Text(
                                        value="Sunflower",
                                        size=20,
                                        expand=True
                                    ),
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
        width=COMPONENT_SIZE,
        height=COMPONENT_SIZE,
        controls=make_seed_controls(
            compute_seeds(MAX_SEEDS // 2),
            animated=True,
        ),
    )
    button = ft.Button(
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.PINK_ACCENT_400,
        content="¡Florece!",
        on_click=open_sunflower,
        align=ft.Alignment.CENTER,
    )
    
    return ft.SafeArea(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                flower_preview, 
                button
            ],
        ),
    )

def timer_animation(callback):
    DIALOG_WIDTH = 760
    DIALOG_HEIGHT = 620

    def open_timer(event: ft.Event[ft.Button]):
        page = event.control.page
        state = {
            "elapsed": 0,
            "started_at": 0.0,
            "running": False,
            "closed": False,
            "task": None,
        }

        def format_hhmmss(seconds: int) -> str:
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"

        def elapsed_seconds() -> int:
            if state["running"]:
                return state["elapsed"] + int(
                    time.monotonic() - state["started_at"]
                )
            return state["elapsed"]

        timer_text = ft.Text(
            "00:00:00",
            size=30,
            weight=ft.FontWeight.BOLD,
        )
        start_button = ft.FilledButton(
            content="Iniciar",
            icon=ft.Icons.PLAY_ARROW,
        )
        stop_button = ft.TextButton(
            content="Detener",
            icon=ft.Icons.STOP,
            disabled=True,
        )

        def refresh():
            timer_text.value = format_hhmmss(elapsed_seconds())
            start_button.content = "Pausar" if state["running"] else "Iniciar"
            start_button.icon = (
                ft.Icons.PAUSE if state["running"] else ft.Icons.PLAY_ARROW
            )
            stop_button.disabled = (
                not state["running"] and state["elapsed"] == 0
            )
            timer_text.update()
            start_button.update()
            stop_button.update()

        async def tick():
            while not state["closed"]:
                if state["running"]:
                    timer_text.value = format_hhmmss(elapsed_seconds())
                    timer_text.update()
                await asyncio.sleep(1)

        def toggle_timer(_event: ft.Event[ft.FilledButton]):
            if state["running"]:
                state["elapsed"] = elapsed_seconds()
                state["running"] = False
            else:
                state["started_at"] = time.monotonic()
                state["running"] = True
                task = state["task"]
                if task is None or task.done():
                    state["task"] = page.run_task(tick)
            refresh()

        def stop_timer(_event: ft.Event[ft.TextButton]):
            state["running"] = False
            state["elapsed"] = 0
            refresh()

        start_button.on_click = toggle_timer
        stop_button.on_click = stop_timer

        def close_timer(_event: ft.Event[ft.IconButton]):
            state["closed"] = True
            task = state["task"]
            if task is not None:
                task.cancel()
            page.pop_dialog()
            callback(inspect.getsource(timer_animation))

        close_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            tooltip="Cerrar temporizador",
            on_click=close_timer,
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
                                    ft.Text("Timer", size=20, expand=True),
                                    close_button,
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    spacing=20,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        timer_text,
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            controls=[
                                                start_button, 
                                                stop_button
                                            ],
                                        ),
                                    ],
                                ),
                                alignment=ft.Alignment.CENTER,
                                expand=True,
                            ),
                        ],
                    ),
                ),
            ),
        )
        callback(inspect.getsource(timer_animation))

    icon_timer = ft.Container(
        width=COMPONENT_SIZE,
        height=COMPONENT_SIZE,
        content=ft.Icon(
            ft.Icons.TIMER,
            size=90,
            color=ft.Colors.WHITE_54,
        ),
        alignment=ft.Alignment.CENTER,
    )
    button = ft.Button(
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.PINK_ACCENT_400,
        content="¡Apúrate!",
        on_click=open_timer,
        align=ft.Alignment.CENTER,
    )
    
    return ft.SafeArea(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                icon_timer,
                button
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
        width=COMPONENT_SIZE,
        height=COMPONENT_SIZE,
        spacing=3,
        run_spacing=3,
        controls=[
            ft.Container(
                bgcolor=random.choice(palette),
                border_radius=4,
                animate=ft.Animation(
                    duration=400,
                    curve=ft.AnimationCurve.EASE_IN_OUT
                ),
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
                ft.Button(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.PINK_ACCENT_400,
                    content="Resolver Cubo",
                    on_click=enter_rubik_ui),
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
        width=COMPONENT_SIZE,
        height=COMPONENT_SIZE,
        spacing=3,
        run_spacing=3,
        controls=[
            ft.Container(
                bgcolor=random.choice(palette),
                border_radius=4,
                animate=ft.Animation(
                    duration=400,
                    curve=ft.AnimationCurve.EASE_IN_OUT
                ),
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
                ft.Button(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.PINK_ACCENT_400,
                    content="Resolver Cubo",
                    on_click=enter_rubik_ui),
            ],
        ),
    )

def heart_animation(callback):
    def animate_heart(e: ft.Event[ft.Button]):
        is_broken = container.border_radius == 75
        container.border_radius = 10 if is_broken else 75
        container.bgcolor = ft.Colors.RED_300 if is_broken else ft.Colors.RED_600
        container.update()
        callback(inspect.getsource(heart_animation))

    return ft.SafeArea(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                container := ft.Container(
                    width=COMPONENT_SIZE,
                    height=COMPONENT_SIZE,
                    bgcolor=ft.Colors.RED_600,
                    border_radius=75,
                    animate=ft.Animation(
                        duration=DEFAULT_ANIMATION_DURATION_MS,
                        curve=ft.AnimationCurve.BOUNCE_OUT,
                    ),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(
                        ft.Icons.FAVORITE, 
                        size=60,
                        color=ft.Colors.WHITE
                    ),
                ),
                ft.Button(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.PINK_ACCENT_400,
                    content="¡Rómpeme!",
                    on_click=animate_heart
                ),
            ],
        ),
    )

def phone_animation(callback):
    def animate_phone(e: ft.Event[ft.Button]):
        # Alterna el zoom (escala entre 1.0 y 1.3)
        container.scale = 1.3 if container.scale == 1.0 else 1.0
        container.update()
        callback(inspect.getsource(phone_animation))
        
    return ft.SafeArea(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                container := ft.Container(
                    width=COMPONENT_SIZE,
                    height=COMPONENT_SIZE,
                    bgcolor=ft.Colors.TEAL_400,
                    border_radius=30,
                    scale=1.0,
                    animate_scale=ft.Animation(
                        duration=DEFAULT_ANIMATION_DURATION_MS,
                        curve=ft.AnimationCurve.EASE_IN_OUT,
                    ),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(
                        ft.Icons.PHONE,
                        size=60,
                        color=ft.Colors.WHITE)
                ),
                ft.Button(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.PINK_ACCENT_400,
                    content="¡Llámame!",
                    on_click=animate_phone
                ),
            ],
        ),
    )

def ball_animation(callback):
    def animate_ball(e: ft.Event[ft.Button]):
        # Secuencia de rebotes sostenidos con transformación de forma (Pelota <-> Triángulo)
        for _ in range(3):
            # Transforma a triángulo y salta alto
            container.border_radius = 0
            container.bgcolor = ft.Colors.PURPLE_ACCENT
            container.content = ft.Icon(ft.Icons.CHANGE_HISTORY, size=60, color=ft.Colors.WHITE)
            container.offset = ft.Offset(0, -0.5)
            container.update()
            time.sleep(0.15)
            
            container.offset = ft.Offset(0, 0)
            container.update()
            time.sleep(0.15)
            
            # Regresa a pelota (círculo) y da un rebote medio
            container.border_radius = COMPONENT_SIZE / 2
            container.bgcolor = ft.Colors.ORANGE_ACCENT
            container.content = ft.Icon(ft.Icons.SPORTS_BASKETBALL, size=60, color=ft.Colors.WHITE)
            container.offset = ft.Offset(0, -0.3)
            container.update()
            time.sleep(0.12)
            
            container.offset = ft.Offset(0, 0)
            container.update()
            time.sleep(0.12)

        callback(inspect.getsource(ball_animation))
     
    return ft.SafeArea(
        content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                container := ft.Container(
                    width=COMPONENT_SIZE,
                    height=COMPONENT_SIZE,
                    bgcolor=ft.Colors.ORANGE_ACCENT,
                    border_radius=COMPONENT_SIZE / 2,
                    offset=ft.Offset(0, 0),
                    animate_offset=ft.Animation(
                        duration=120,
                        curve=ft.AnimationCurve.EASE_OUT,
                    ),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(
                        icon=ft.Icons.SPORTS_BASKETBALL,
                        size=60,
                        color=ft.Colors.WHITE
                    ),
                ),
                ft.Button(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.PINK_ACCENT_400,
                    content="¡Bótame!",
                    on_click=animate_ball
                ),
            ],
        )
    )

def sound_box_component(callback):
    def play_audio(e):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        audio_path = os.path.join(base_dir, "assets", "song.mp3")

        callback(inspect.getsource(sound_box_component))

        try:
            os.startfile(audio_path)
        except Exception as ex:
            print(f"Error al reproducir audio: {ex}")

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(
                    ft.Icons.MUSIC_NOTE, 
                    color=ft.Colors.WHITE, 
                    size=40
                ),
                ft.Text(
                    value="Caja de Sonidos",
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        bgcolor=ft.Colors.PINK_700,
        border_radius=ft.BorderRadius.all(15),
        on_click=play_audio,
        ink=True
    )

def color_palette_component(callback):
    def gesture_detector(data: str,
                         txt: str,
                         color_a: ft.Colors,
                         color_b: ft.Colors,
                         color_c: ft.Colors):
        return ft.GestureDetector(
            on_tap=change_theme,
            data=data,
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(
                            value=txt,
                            size=10,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Row(
                            controls=[
                                ft.Container(
                                    width=10,
                                    height=10,
                                    bgcolor=color_a,
                                    border_radius=2,
                                ),
                                ft.Container(
                                    width=10,
                                    height=10,
                                    bgcolor=color_b,
                                    border_radius=2,
                                ),
                                ft.Container(
                                    width=10,
                                    height=10,
                                    bgcolor=color_c,
                                    border_radius=2,
                                ),
                            ],
                            spacing=2,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=ft.Colors.PURPLE_900,
                padding=6,
                border_radius=5,
                ink=True,
            ),
        )

    def change_theme(e):
        palette_type = e.control.data
        page = e.page

        if palette_type == "color1":
            card_container.bgcolor = ft.Colors.BLUE_GREY_800
            page.bgcolor = ft.Colors.BLUE_900
        elif palette_type == "color2":
            card_container.bgcolor = ft.Colors.DEEP_PURPLE_800
            page.bgcolor = ft.Colors.INDIGO_900
        elif palette_type == "color3":
            card_container.bgcolor = ft.Colors.BROWN_800
            page.bgcolor = ft.Colors.DEEP_ORANGE_900

        card_container.update()
        page.update()
        callback(inspect.getsource(color_palette_component))

    return ft.SafeArea(
        card_container := ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                icon=ft.Icons.PALETTE, 
                                color=ft.Colors.WHITE, 
                                size=22
                            ),
                            ft.Text(
                                value="Paleta Colores",
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD,
                                size=12,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    gesture_detector(
                        "color1",
                        "Color 1",
                        ft.Colors.BLUE_400,
                        ft.Colors.ORANGE_400,
                        ft.Colors.RED_400
                    ),
                    gesture_detector(
                        "color2",
                        "Color 2",
                        ft.Colors.BLUE_400,
                        ft.Colors.CYAN_400,
                        ft.Colors.PURPLE_400
                    ),
                    gesture_detector(
                        "color3",
                        "Color 3",
                        ft.Colors.RED_400,
                        ft.Colors.ORANGE_400,
                        ft.Colors.AMBER_400
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=4,
            ),
            bgcolor=ft.Colors.PURPLE_700,
            border_radius=ft.BorderRadius.all(15),
            padding=8,
            on_click=None,
            ink=True,
        ),
    )

def clock_component(callback):
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%d/%m/%Y")


    def show_clock_info(e):
        callback(inspect.getsource(clock_component))

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(
                    icon=ft.Icons.ACCESS_TIME,
                    color=ft.Colors.WHITE,
                    size=30),
                ft.Text(
                    value=time_str,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                    size=16),
                ft.Text(
                    value=date_str,
                    color=ft.Colors.WHITE_70,
                    size=12)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        bgcolor=ft.Colors.INDIGO_700,
        border_radius=ft.BorderRadius.all(15),
        on_click=show_clock_info,
        ink=True
    )