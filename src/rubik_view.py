import asyncio
import math
import time
import cv2
import flet as ft
import flet.canvas as cv
import kociemba
from camera_scanner import (
    DEFAULT_LAB_REFS,
    SCAN_ORDER,
    find_mac_camera_index,
    open_camera_capture,
    process_camera_frame,
    reclassify_all_faces,
)

from camera_scanner import SCAN_ORDER, find_mac_camera_index, process_camera_frame
from sound_fx import play_turn_click, play_victory_sound

COLORS = {
    "U": ft.Colors.WHITE,         # Arriba (Blanco)
    "R": ft.Colors.RED_500,       # Derecha (Rojo)
    "F": ft.Colors.GREEN_500,     # Frente (Verde)
    "D": ft.Colors.YELLOW_400,    # Abajo (Amarillo)
    "L": ft.Colors.ORANGE_500,    # Izquierda (Naranja)
    "B": ft.Colors.BLUE_500,      # Atrás (Azul)
}

FACE_NAMES = {
    "U": "Blanco",
    "R": "Rojo",
    "F": "Verde",
    "D": "Amarillo",
    "L": "Naranja",
    "B": "Azul",
}

MOVE_EXPLANATIONS = {
    "U": "Gira cara BLANCA (Arriba) 90° horario",
    "U'": "Gira cara BLANCA (Arriba) 90° antihorario",
    "U2": "Gira cara BLANCA (Arriba) 180°",
    "D": "Gira cara AMARILLA (Abajo) 90° horario",
    "D'": "Gira cara AMARILLA (Abajo) 90° antihorario",
    "D2": "Gira cara AMARILLA (Abajo) 180°",
    "F": "Gira cara VERDE (Frente) 90° horario",
    "F'": "Gira cara VERDE (Frente) 90° antihorario",
    "F2": "Gira cara VERDE (Frente) 180°",
    "B": "Gira cara AZUL (Atrás) 90° horario",
    "B'": "Gira cara AZUL (Atrás) 90° antihorario",
    "B2": "Gira cara AZUL (Atrás) 180°",
    "L": "Gira cara NARANJA (Izquierda) 90° horario",
    "L'": "Gira cara NARANJA (Izquierda) 90° antihorario",
    "L2": "Gira cara NARANJA (Izquierda) 180°",
    "R": "Gira cara ROJA (Derecha) 90° horario",
    "R'": "Gira cara ROJA (Derecha) 90° antihorario",
    "R2": "Gira cara ROJA (Derecha) 180°",
}

SPEED_CONFIGS = {
    "lento": {"step_delay": 0.055, "pause_between": 0.90, "frames": 20},
    "normal": {"step_delay": 0.025, "pause_between": 0.35, "frames": 12},
    "rapido": {"step_delay": 0.012, "pause_between": 0.12, "frames": 8},
}


def invert_move(move: str) -> str:
    if move.endswith("'"):
        return move[0]
    elif move.endswith("2"):
        return move
    return move + "'"


class RubikState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.faces = {face: [face] * 9 for face in COLORS}

    def rotate_face_cw(self, face):
        f = self.faces[face]
        self.faces[face] = [f[6], f[3], f[0], f[7], f[4], f[1], f[8], f[5], f[2]]

    def apply_single_move(self, base_move: str):
        if base_move == "F":
            self.rotate_face_cw("F")
            u, r, d, l = self.faces["U"], self.faces["R"], self.faces["D"], self.faces["L"]
            temp = [u[6], u[7], u[8]]
            u[6], u[7], u[8] = l[8], l[5], l[2]
            l[2], l[5], l[8] = d[0], d[1], d[2]
            d[0], d[1], d[2] = r[6], r[3], r[0]
            r[0], r[3], r[6] = temp[0], temp[1], temp[2]

        elif base_move == "U":
            self.rotate_face_cw("U")
            f, r, b, l = self.faces["F"], self.faces["R"], self.faces["B"], self.faces["L"]
            temp = f[:3]
            f[:3], r[:3], b[:3], l[:3] = r[:3], b[:3], l[:3], temp

        elif base_move == "R":
            self.rotate_face_cw("R")
            u, f, d, b = self.faces["U"], self.faces["F"], self.faces["D"], self.faces["B"]
            temp = [u[2], u[5], u[8]]
            u[2], u[5], u[8] = f[2], f[5], f[8]
            f[2], f[5], f[8] = d[2], d[5], d[8]
            d[2], d[5], d[8] = b[6], b[3], b[0]
            b[0], b[3], b[6] = temp[2], temp[1], temp[0]

        elif base_move == "L":
            self.rotate_face_cw("L")
            u, f, d, b = self.faces["U"], self.faces["F"], self.faces["D"], self.faces["B"]
            temp = [u[0], u[3], u[6]]
            u[0], u[3], u[6] = b[8], b[5], b[2]
            b[2], b[5], b[8] = d[6], d[3], d[0]
            d[0], d[3], d[6] = f[0], f[3], f[6]
            f[0], f[3], f[6] = temp[0], temp[1], temp[2]

        elif base_move == "D":
            self.rotate_face_cw("D")
            f, r, b, l = self.faces["F"], self.faces["R"], self.faces["B"], self.faces["L"]
            temp = f[6:]
            f[6:], l[6:], b[6:], r[6:] = l[6:], b[6:], r[6:], temp

        elif base_move == "B":
            self.rotate_face_cw("B")
            u, r, d, l = self.faces["U"], self.faces["R"], self.faces["D"], self.faces["L"]
            temp = [u[0], u[1], u[2]]
            u[0], u[1], u[2] = r[2], r[5], r[8]
            r[2], r[5], r[8] = d[8], d[7], d[6]
            d[6], d[7], d[8] = l[0], l[3], l[6]
            l[0], l[3], l[6] = temp[2], temp[1], temp[0]

    def execute_notation(self, notation: str):
        base = notation[0]
        if notation.endswith("'"):
            for _ in range(3):
                self.apply_single_move(base)
        elif notation.endswith("2"):
            for _ in range(2):
                self.apply_single_move(base)
        else:
            self.apply_single_move(base)

    def to_kociemba_string(self) -> str:
        order = ["U", "R", "F", "D", "L", "B"]
        return "".join("".join(self.faces[f]) for f in order)


def rotate_point_axis(x: float, y: float, z: float, axis: str, angle: float):
    c, s = math.cos(angle), math.sin(angle)
    if axis == "x":
        return x, y * c - z * s, y * s + z * c
    elif axis == "y":
        return x * c + z * s, y, -x * s + z * c
    elif axis == "z":
        return x * c - y * s, x * s + y * c, z
    return x, y, z


def get_slice_rotation_params(move: str):
    base = move[0]
    cw_signs = {
        "U": ("y", 1, -1),
        "D": ("y", -1, 1),
        "R": ("x", 1, -1),
        "L": ("x", -1, 1),
        "F": ("z", 1, -1),
        "B": ("z", -1, 1),
    }
    axis, layer, cw_sign = cw_signs[base]
    if move.endswith("'"):
        turns = -cw_sign
    elif move.endswith("2"):
        turns = 2 * cw_sign
    else:
        turns = cw_sign
    return axis, layer, turns * (math.pi / 2.0)


def map_face_uv(face: str, u: float, v: float):
    if face == "F":
        return (u, v, 1.0)
    elif face == "B":
        return (-u, v, -1.0)
    elif face == "U":
        return (u, 1.0, -v)
    elif face == "D":
        return (u, -1.0, v)
    elif face == "R":
        return (1.0, v, -u)
    elif face == "L":
        return (-1.0, v, u)


def get_cubie_coords(face: str, row: int, col: int):
    u = col - 1
    v = 1 - row
    if face == "F":
        return (u, v, 1)
    elif face == "B":
        return (-u, v, -1)
    elif face == "U":
        return (u, 1, -v)
    elif face == "D":
        return (u, -1, v)
    elif face == "R":
        return (1, v, -u)
    elif face == "L":
        return (-1, v, u)


def build_static_faces_cache():
    cache = {}
    gap = 0.055
    step = 2.0 / 3.0
    for face in ["U", "D", "F", "B", "L", "R"]:
        base_3d = [
            map_face_uv(face, -1.0, 1.0),
            map_face_uv(face, 1.0, 1.0),
            map_face_uv(face, 1.0, -1.0),
            map_face_uv(face, -1.0, -1.0),
        ]
        stickers_3d = []
        for idx in range(9):
            row, col = divmod(idx, 3)
            u0 = -1.0 + col * step + gap
            u1 = -1.0 + (col + 1) * step - gap
            v0 = 1.0 - row * step - gap
            v1 = 1.0 - (row + 1) * step + gap
            stickers_3d.append((
                idx,
                [
                    map_face_uv(face, u0, v0),
                    map_face_uv(face, u1, v0),
                    map_face_uv(face, u1, v1),
                    map_face_uv(face, u0, v1),
                ],
            ))
        cache[face] = (base_3d, stickers_3d)
    return cache


def build_cubies_list():
    sticker_lookup = {}
    for face in ["U", "D", "F", "B", "L", "R"]:
        for idx in range(9):
            row, col = divmod(idx, 3)
            coords = get_cubie_coords(face, row, col)
            sticker_lookup[(coords[0], coords[1], coords[2], face)] = (face, idx)

    cubies = []
    step = 2.0 / 3.0
    inset = 0.055

    for cx in (-1, 0, 1):
        for cy in (-1, 0, 1):
            for cz in (-1, 0, 1):
                if cx == 0 and cy == 0 and cz == 0:
                    continue
                x0, x1 = cx * step - step / 2.0, cx * step + step / 2.0
                y0, y1 = cy * step - step / 2.0, cy * step + step / 2.0
                z0, z1 = cz * step - step / 2.0, cz * step + step / 2.0

                black_faces = [
                    ("F", [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)]),
                    ("B", [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)]),
                    ("U", [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]),
                    ("D", [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)]),
                    ("R", [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)]),
                    ("L", [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)]),
                ]

                stickers = []
                for f_dir, _ in black_faces:
                    key = (cx, cy, cz, f_dir)
                    if key in sticker_lookup:
                        face_code, idx = sticker_lookup[key]
                        sx0, sx1 = x0 + inset, x1 - inset
                        sy0, sy1 = y0 + inset, y1 - inset
                        sz0, sz1 = z0 + inset, z1 - inset
                        eps = 0.004
                        if f_dir == "F":
                            quad = [(sx0, sy1, z1 + eps), (sx1, sy1, z1 + eps), (sx1, sy0, z1 + eps), (sx0, sy0, z1 + eps)]
                        elif f_dir == "B":
                            quad = [(sx1, sy1, z0 - eps), (sx0, sy1, z0 - eps), (sx0, sy0, z0 - eps), (sx1, sy0, z0 - eps)]
                        elif f_dir == "U":
                            quad = [(sx0, y1 + eps, sz0), (sx1, y1 + eps, sz0), (sx1, y1 + eps, sz1), (sx0, y1 + eps, sz1)]
                        elif f_dir == "D":
                            quad = [(sx0, y0 - eps, sz1), (sx1, y0 - eps, sz1), (sx1, y0 - eps, sz0), (sx0, y0 - eps, sz0)]
                        elif f_dir == "R":
                            quad = [(x1 + eps, sy1, sz1), (x1 + eps, sy1, sz0), (x1 + eps, sy0, sz0), (x1 + eps, sy0, sz1)]
                        elif f_dir == "L":
                            quad = [(x0 - eps, sy1, sz0), (x0 - eps, sy1, sz1), (x0 - eps, sy0, sz1), (x0 - eps, sy0, sz0)]
                        stickers.append((face_code, idx, quad))

                cubies.append({
                    "coords": (cx, cy, cz),
                    "black_faces": [q for _, q in black_faces],
                    "stickers": stickers,
                })
    return cubies


STATIC_FACES_CACHE = build_static_faces_cache()
CUBIES_MODEL = build_cubies_list()

BLACK_FILL_PAINT = ft.Paint(color=ft.Colors.BLACK, style=ft.PaintingStyle.FILL)
CENTER_DOT_PAINT = ft.Paint(color=ft.Colors.BLACK_54)
STICKER_PAINTS = {
    code: ft.Paint(color=col, style=ft.PaintingStyle.FILL)
    for code, col in COLORS.items()
}


def make_quad_path(pts_2d, paint):
    return cv.Path(
        elements=[
            cv.Path.MoveTo(pts_2d[0][0], pts_2d[0][1]),
            cv.Path.LineTo(pts_2d[1][0], pts_2d[1][1]),
            cv.Path.LineTo(pts_2d[2][0], pts_2d[2][1]),
            cv.Path.LineTo(pts_2d[3][0], pts_2d[3][1]),
            cv.Path.Close(),
        ],
        paint=paint,
    )


def point_in_poly(px, py, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
        j = i
    return inside


def open_rubik_interface(page: ft.Page):
    cube = RubikState()
    camera = {"yaw": -0.58, "pitch": 0.46}
    slice_anim = {"axis": None, "layer": 0, "angle": 0.0}
    selected_brush = ["R"]
    solution_steps = []
    step_index = [0]
    current_speed = ["normal"]
    sound_enabled = [True]
    is_animating = [False]
    is_turning = [False]
    is_open = [True]
    last_render_time = [0.0]
    visible_polygons = []
    brush_boxes = {}

    # Estado del escáner de cámara integrado
    cam_state = {
        "active": False,
        "cam_idx": 0,
        "scan_step": 0,
        "scanned_faces": {},
        "raw_labs": {},
        "calibrated_labs": dict(DEFAULT_LAB_REFS),
        "latest_9": ["U"] * 9,
        "latest_labs": [],
    }
    status_banner = ft.Text(
        "Arrastra el cubo 3D • Pinta manualmente o escanea tu cubo con la cámara",
        size=13,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.AMBER_300,
        text_align=ft.TextAlign.CENTER,
    )

    step_instruction = ft.Text(
        "",
        size=14,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.CYAN_ACCENT_200,
        text_align=ft.TextAlign.CENTER,
    )

    canvas = cv.Canvas(width=360, height=280, shapes=[])

    # Visor de cámara nativo dentro de Flet
    camera_preview = ft.Image(
        src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
        width=285,
        height=285,
        fit=ft.BoxFit.COVER,
        gapless_playback=True,
        border_radius=12,
    )

    cam_capture_btn = ft.FilledButton(
        "Capturar Cara (Espacio)",
        icon=ft.Icons.CAMERA,
        bgcolor=ft.Colors.GREEN_600,
        color=ft.Colors.WHITE,
    )
    cam_prev_btn = ft.OutlinedButton("Anterior", icon=ft.Icons.SKIP_PREVIOUS)
    cam_switch_btn = ft.OutlinedButton("Cambiar Cámara", icon=ft.Icons.CAMERASWITCH)
    cam_cancel_btn = ft.OutlinedButton("Cancelar", icon=ft.Icons.CLOSE)

    # Ángulos exactos (yaw, pitch) según nuestra matriz de proyección para enfocar cada cara
    # con una ligera inclinación para que se vea el color de la cara vecina de referencia
    FACE_3D_ANGLES = {
        "F": (0.0, 0.35),            # 1/6: Verde al frente (Blanco arriba)
        "R": (-math.pi / 2, 0.35),   # 2/6: Rojo al frente (Blanco arriba)
        "B": (-math.pi, 0.35),       # 3/6: Azul al frente (Blanco arriba)
        "L": (-1.5 * math.pi, 0.35), # 4/6: Naranja al frente (Blanco arriba)
        "U": (0.0, 1.18),            # 5/6: Blanco al frente (Verde abajo)
        "D": (0.0, -1.18),           # 6/6: Amarillo al frente (Verde arriba)
    }

    mini_cam = {"yaw": 0.0, "pitch": 0.35, "manual_orbit": False}
    mini_cube_canvas = cv.Canvas(width=200, height=200, shapes=[])

    def on_pan_mini_cube(e: ft.DragUpdateEvent):
        mini_cam["manual_orbit"] = True
        dx = e.local_delta.x if e.local_delta else 0
        dy = e.local_delta.y if e.local_delta else 0
        mini_cam["yaw"] += dx * 0.02
        mini_cam["pitch"] = max(-1.35, min(1.35, mini_cam["pitch"] + dy * 0.02))
        if cam_state["active"] and cam_state["scan_step"] < len(SCAN_ORDER):
            active_face, _ = SCAN_ORDER[cam_state["scan_step"]]
            render_mini_3d_guide(active_face, cam_state["latest_9"], cam_state["scanned_faces"])
            if mini_cube_canvas.page:
                mini_cube_canvas.update()

    def render_mini_3d_guide(active_face: str, live_9: list[str], saved_faces: dict[str, list[str]]):
        yaw, pitch = mini_cam["yaw"], mini_cam["pitch"]
        cyaw, syaw = math.cos(yaw), math.sin(yaw)
        cpitch, spitch = math.cos(pitch), math.sin(pitch)

        def proj_mini(x, y, z):
            x1 = x * cyaw + z * syaw
            z1 = -x * syaw + z * cyaw
            y2 = y * cpitch - z1 * spitch
            z2 = y * spitch + z1 * cpitch
            factor = 5.0 / (5.0 - z2)
            return 100.0 + x1 * 48.0 * factor, 100.0 - y2 * 48.0 * factor, z2

        visible_faces = []
        for face, (base_3d, stickers_3d) in STATIC_FACES_CACHE.items():
            proj_base = [proj_mini(x, y, z) for x, y, z in base_3d]
            pts_2d = [(p[0], p[1]) for p in proj_base]
            ax, ay = pts_2d[1][0] - pts_2d[0][0], pts_2d[1][1] - pts_2d[0][1]
            bx, by = pts_2d[2][0] - pts_2d[0][0], pts_2d[2][1] - pts_2d[0][1]
            if ax * by - ay * bx > 0:
                avg_z = sum(p[2] for p in proj_base) / 4.0
                visible_faces.append((avg_z, face, pts_2d, stickers_3d))

        visible_faces.sort(key=lambda item: item[0])
        shapes = []

        for _, face, base_2d, stickers_3d in visible_faces:
            shapes.append(make_quad_path(base_2d, BLACK_FILL_PAINT))
            if face == active_face:
                face_colors = live_9
            elif face in saved_faces:
                face_colors = saved_faces[face]
            else:
                face_colors = [None] * 9
                face_colors[4] = face

            for idx, s_3d in stickers_3d:
                s_2d = [(proj_mini(x, y, z)[0], proj_mini(x, y, z)[1]) for x, y, z in s_3d]
                c_code = face_colors[idx]
                paint = STICKER_PAINTS[c_code] if c_code else ft.Paint(color=ft.Colors.GREY_800, style=ft.PaintingStyle.FILL)
                shapes.append(make_quad_path(s_2d, paint))
                if idx == 4:
                    cx_s = (s_2d[0][0] + s_2d[2][0]) * 0.5
                    cy_s = (s_2d[0][1] + s_2d[2][1]) * 0.5
                    shapes.append(cv.Circle(x=cx_s, y=cy_s, radius=3.0, paint=CENTER_DOT_PAINT))

        mini_cube_canvas.shapes = shapes

    camera_panel = ft.Column(
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=24,
                controls=[
                    camera_preview,
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                        controls=[
                            ft.Text(
                                "Guía 3D en vivo:",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.CYAN_ACCENT_200,
                            ),
                            ft.GestureDetector(
                                on_pan_update=on_pan_mini_cube,
                                content=mini_cube_canvas,
                            ),
                            ft.Text(
                                "Arrastra para girar libremente",
                                size=11,
                                color=ft.Colors.WHITE_70,
                            ),
                        ],
                    ),
                ],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    cam_capture_btn,
                    cam_prev_btn,
                    cam_switch_btn,
                    cam_cancel_btn,
                ],
            ),
        ],
    )

    prev_step_btn = ft.OutlinedButton("Anterior", icon=ft.Icons.SKIP_PREVIOUS, visible=False)
    pause_resume_btn = ft.FilledButton("Pausar", icon=ft.Icons.PAUSE, visible=False)
    next_step_btn = ft.OutlinedButton("Siguiente", icon=ft.Icons.SKIP_NEXT, visible=False)

    def on_speed_change(e):
        if e.control.selected:
            current_speed[0] = list(e.control.selected)[0]

    speed_selector = ft.SegmentedButton(
        selected=["normal"],
        allow_multiple_selection=False,
        on_change=on_speed_change,
        segments=[
            ft.Segment(value="lento", label=ft.Text("Lento")),
            ft.Segment(value="normal", label=ft.Text("Normal")),
            ft.Segment(value="rapido", label=ft.Text("Rápido")),
        ],
    )

    speed_row = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        visible=False,
        controls=[
            ft.Text("Velocidad:", size=12, color=ft.Colors.WHITE_70),
            speed_selector,
        ],
    )

    def update_playback_controls():
        has_steps = len(solution_steps) > 0 and not cam_state["active"]
        prev_step_btn.visible = has_steps
        next_step_btn.visible = has_steps
        speed_row.visible = has_steps
        pause_resume_btn.visible = has_steps and step_index[0] < len(solution_steps)

        prev_step_btn.disabled = is_animating[0] or is_turning[0] or step_index[0] <= 0
        next_step_btn.disabled = is_animating[0] or is_turning[0] or step_index[0] >= len(solution_steps)

        if is_animating[0]:
            pause_resume_btn.text = "Pausar"
            pause_resume_btn.icon = ft.Icons.PAUSE
        else:
            pause_resume_btn.text = "Reanudar"
            pause_resume_btn.icon = ft.Icons.PLAY_ARROW

    def render_3d(only_canvas: bool = False):
        cyaw, syaw = math.cos(camera["yaw"]), math.sin(camera["yaw"])
        cpitch, spitch = math.cos(camera["pitch"]), math.sin(camera["pitch"])

        def proj(x, y, z):
            x1 = x * cyaw + z * syaw
            z1 = -x * syaw + z * cyaw
            y2 = y * cpitch - z1 * spitch
            z2 = y * spitch + z1 * cpitch
            factor = 5.0 / (5.0 - z2)
            return 180.0 + x1 * 82.0 * factor, 140.0 - y2 * 82.0 * factor, z2

        visible_polygons.clear()
        shapes = []

        if slice_anim["axis"] is None:
            visible_faces = []
            for face, (base_3d, stickers_3d) in STATIC_FACES_CACHE.items():
                proj_base = [proj(x, y, z) for x, y, z in base_3d]
                pts_2d = [(p[0], p[1]) for p in proj_base]
                ax, ay = pts_2d[1][0] - pts_2d[0][0], pts_2d[1][1] - pts_2d[0][1]
                bx, by = pts_2d[2][0] - pts_2d[0][0], pts_2d[2][1] - pts_2d[0][1]
                if ax * by - ay * bx > 0:
                    avg_z = sum(p[2] for p in proj_base) / 4.0
                    visible_faces.append((avg_z, face, pts_2d, stickers_3d))

            visible_faces.sort(key=lambda item: item[0])

            for _, face, base_2d, stickers_3d in visible_faces:
                shapes.append(make_quad_path(base_2d, BLACK_FILL_PAINT))
                face_colors = cube.faces[face]
                for idx, s_3d in stickers_3d:
                    s_2d = [(proj(x, y, z)[0], proj(x, y, z)[1]) for x, y, z in s_3d]
                    shapes.append(make_quad_path(s_2d, STICKER_PAINTS[face_colors[idx]]))
                    if idx == 4:
                        cx_s = (s_2d[0][0] + s_2d[2][0]) * 0.5
                        cy_s = (s_2d[0][1] + s_2d[2][1]) * 0.5
                        shapes.append(cv.Circle(x=cx_s, y=cy_s, radius=3.5, paint=CENTER_DOT_PAINT))
                    visible_polygons.append((face, idx, s_2d))
        else:
            axis = slice_anim["axis"]
            layer = slice_anim["layer"]
            angle = slice_anim["angle"]
            draw_items = []

            for cubie in CUBIES_MODEL:
                cx, cy, cz = cubie["coords"]
                is_rotating = (
                    (axis == "x" and cx == layer)
                    or (axis == "y" and cy == layer)
                    or (axis == "z" and cz == layer)
                )

                for quad in cubie["black_faces"]:
                    p_list = (
                        [proj(*rotate_point_axis(x, y, z, axis, angle)) for x, y, z in quad]
                        if is_rotating
                        else [proj(x, y, z) for x, y, z in quad]
                    )
                    pts_2d = [(p[0], p[1]) for p in p_list]
                    ax, ay = pts_2d[1][0] - pts_2d[0][0], pts_2d[1][1] - pts_2d[0][1]
                    bx, by = pts_2d[2][0] - pts_2d[0][0], pts_2d[2][1] - pts_2d[0][1]
                    if ax * by - ay * bx > 0:
                        avg_z = sum(p[2] for p in p_list) * 0.25
                        draw_items.append((avg_z, False, pts_2d))

                for face_code, idx, quad in cubie["stickers"]:
                    p_list = (
                        [proj(*rotate_point_axis(x, y, z, axis, angle)) for x, y, z in quad]
                        if is_rotating
                        else [proj(x, y, z) for x, y, z in quad]
                    )
                    pts_2d = [(p[0], p[1]) for p in p_list]
                    ax, ay = pts_2d[1][0] - pts_2d[0][0], pts_2d[1][1] - pts_2d[0][1]
                    bx, by = pts_2d[2][0] - pts_2d[0][0], pts_2d[2][1] - pts_2d[0][1]
                    if ax * by - ay * bx > 0:
                        avg_z = sum(p[2] for p in p_list) * 0.25 + 0.002
                        draw_items.append((avg_z, True, (face_code, idx, pts_2d)))

            draw_items.sort(key=lambda item: item[0])

            for _, is_sticker, payload in draw_items:
                if not is_sticker:
                    shapes.append(make_quad_path(payload, BLACK_FILL_PAINT))
                else:
                    face_code, idx, pts_2d = payload
                    color_code = cube.faces[face_code][idx]
                    shapes.append(make_quad_path(pts_2d, STICKER_PAINTS[color_code]))
                    if idx == 4:
                        cx_s = (pts_2d[0][0] + pts_2d[2][0]) * 0.5
                        cy_s = (pts_2d[0][1] + pts_2d[2][1]) * 0.5
                        shapes.append(cv.Circle(x=cx_s, y=cy_s, radius=3.5, paint=CENTER_DOT_PAINT))

        canvas.shapes = shapes
        if only_canvas and canvas.page:
            canvas.update()
        else:
            page.update()

    def on_pan_cube(e: ft.DragUpdateEvent):
        dx = e.local_delta.x if e.local_delta else 0
        dy = e.local_delta.y if e.local_delta else 0
        camera["yaw"] += dx * 0.015
        camera["pitch"] = max(-1.35, min(1.35, camera["pitch"] + dy * 0.015))

        now = time.monotonic()
        if now - last_render_time[0] >= 0.016:
            last_render_time[0] = now
            render_3d(only_canvas=True)

    def on_tap_cube(e: ft.TapEvent):
        if is_animating[0] or is_turning[0] or not e.local_position:
            return
        lx, ly = e.local_position.x, e.local_position.y
        for face, idx, pts_2d in reversed(visible_polygons):
            if point_in_poly(lx, ly, pts_2d):
                if idx == 4:
                    status_banner.value = "⚠️ El centro con punto es fijo; define el color de esa cara."
                    status_banner.color = ft.Colors.ORANGE_300
                    page.update()
                    return
                cube.faces[face][idx] = selected_brush[0]
                play_turn_click(sound_enabled[0])
                render_3d(only_canvas=True)
                return

    async def animate_physical_turn(move: str):
        is_turning[0] = True
        axis, layer, target_angle = get_slice_rotation_params(move)
        slice_anim["axis"] = axis
        slice_anim["layer"] = layer

        play_turn_click(sound_enabled[0])

        cfg = SPEED_CONFIGS[current_speed[0]]
        base_steps = cfg["frames"]
        steps = base_steps if not move.endswith("2") else int(base_steps * 1.5)

        for s in range(1, steps + 1):
            if not is_open[0]:
                break
            t = s / steps
            smooth_t = t * t * (3.0 - 2.0 * t)
            slice_anim["angle"] = target_angle * smooth_t
            render_3d(only_canvas=True)
            await asyncio.sleep(SPEED_CONFIGS[current_speed[0]]["step_delay"])

        slice_anim["axis"] = None
        slice_anim["angle"] = 0.0
        cube.execute_notation(move)
        is_turning[0] = False
        render_3d(only_canvas=True)

    async def animate_solution():
        is_animating[0] = True
        update_playback_controls()
        page.update()

        while is_animating[0] and step_index[0] < len(solution_steps) and is_open[0]:
            move = solution_steps[step_index[0]]
            step_instruction.value = (
                f"Paso {step_index[0] + 1}/{len(solution_steps)} ({move}): "
                f"{MOVE_EXPLANATIONS[move]}"
            )
            step_instruction.update()

            await animate_physical_turn(move)
            step_index[0] += 1

            await asyncio.sleep(SPEED_CONFIGS[current_speed[0]]["pause_between"])

        is_animating[0] = False
        update_playback_controls()
        if step_index[0] >= len(solution_steps):
            play_victory_sound(sound_enabled[0])
            step_instruction.value = "🎉 ¡Cubo completamente resuelto!"
            status_banner.value = "Solución finalizada. Puedes retroceder pasos o reiniciar."
            status_banner.color = ft.Colors.GREEN_ACCENT_400
        page.update()

    async def step_backward():
        if is_animating[0] or is_turning[0] or step_index[0] <= 0:
            return
        step_index[0] -= 1
        orig_move = solution_steps[step_index[0]]
        rev_move = invert_move(orig_move)
        step_instruction.value = (
            f"Retrocediendo paso {step_index[0] + 1}/{len(solution_steps)} ({rev_move}): "
            f"{MOVE_EXPLANATIONS[rev_move]}"
        )
        status_banner.value = f"Paso {step_index[0]}/{len(solution_steps)} completados"
        status_banner.color = ft.Colors.AMBER_300
        update_playback_controls()
        page.update()

        await animate_physical_turn(rev_move)
        update_playback_controls()
        page.update()

    async def step_forward():
        if is_animating[0] or is_turning[0] or step_index[0] >= len(solution_steps):
            return
        move = solution_steps[step_index[0]]
        step_instruction.value = (
            f"Paso {step_index[0] + 1}/{len(solution_steps)} ({move}): "
            f"{MOVE_EXPLANATIONS[move]}"
        )
        update_playback_controls()
        page.update()

        await animate_physical_turn(move)
        step_index[0] += 1

        if step_index[0] >= len(solution_steps):
            play_victory_sound(sound_enabled[0])
            step_instruction.value = "🎉 ¡Cubo completamente resuelto!"
            status_banner.value = "Solución finalizada. Puedes retroceder pasos o reiniciar."
            status_banner.color = ft.Colors.GREEN_ACCENT_400
        else:
            status_banner.value = f"Paso {step_index[0]}/{len(solution_steps)} completados"
        update_playback_controls()
        page.update()

    def on_prev_click(e):
        page.run_task(step_backward)

    def on_next_click(e):
        page.run_task(step_forward)

    def toggle_pause_resume(e):
        if is_animating[0]:
            is_animating[0] = False
            update_playback_controls()
            page.update()
        else:
            page.run_task(animate_solution)

    prev_step_btn.on_click = on_prev_click
    next_step_btn.on_click = on_next_click
    pause_resume_btn.on_click = toggle_pause_resume

    # --- Lógica del Escáner de Cámara Nativo ---
    def exit_camera_mode(completed: bool = False):
        cam_state["active"] = False
        camera_panel.visible = False
        cube_view_panel.visible = True
        action_bar.visible = True
        update_playback_controls()
        if completed:
            # Reclasifica los 54 cuadritos usando los 6 centros reales calibrados de tu cubo
            calibrated_faces = reclassify_all_faces(
                cam_state["raw_labs"], cam_state["calibrated_labs"]
            )
            cube.faces = calibrated_faces
            solution_steps.clear()
            step_index[0] = 0
            step_instruction.value = ""
            play_victory_sound(sound_enabled[0])
            status_banner.value = "✅ ¡6 caras calibradas y capturadas! Revisa el cubo 3D y presiona Calcular Solución."
            status_banner.color = ft.Colors.GREEN_ACCENT_400
            render_3d()
        else:
            status_banner.value = "Escaneo cancelado. Puedes pintar manualmente o reintentar."
            status_banner.color = ft.Colors.AMBER_300
            page.update()

    def capture_current_face(e=None):
        if not cam_state["active"]:
            return
        idx = cam_state["scan_step"]
        if idx < len(SCAN_ORDER):
            face_code, _ = SCAN_ORDER[idx]
            cam_state["scanned_faces"][face_code] = list(cam_state["latest_9"])
            if cam_state["latest_labs"]:
                cam_state["raw_labs"][face_code] = list(cam_state["latest_labs"])
                cam_state["calibrated_labs"][face_code] = cam_state["latest_labs"][4]
            play_turn_click(sound_enabled[0])
            cam_state["scan_step"] += 1
            mini_cam["manual_orbit"] = False  # <--- AQUÍ

            if cam_state["scan_step"] >= len(SCAN_ORDER):
                exit_camera_mode(completed=True)
            else:
                _, next_prompt = SCAN_ORDER[cam_state["scan_step"]]
                status_banner.value = f"📷 {next_prompt}"
                page.update()

    def prev_camera_face(e=None):
        if cam_state["active"] and cam_state["scan_step"] > 0:
            cam_state["scan_step"] -= 1
            mini_cam["manual_orbit"] = False  # <--- AQUÍ
            _, prompt = SCAN_ORDER[cam_state["scan_step"]]
            status_banner.value = f"📷 {prompt}"
            page.update()

    def switch_camera_device(e=None):
        cam_state["cam_idx"] = 1 if cam_state["cam_idx"] == 0 else 0
        cam_switch_btn.text = f"Cámara ({cam_state['cam_idx']})"
        page.update()

    cam_capture_btn.on_click = capture_current_face
    cam_prev_btn.on_click = prev_camera_face
    cam_switch_btn.on_click = switch_camera_device
    cam_cancel_btn.on_click = lambda e: exit_camera_mode(completed=False)

    # Capturar con la tecla ESPACIO directamente en Flet
    def on_key_event(e: ft.KeyboardEvent):
        if cam_state["active"] and is_open[0]:
            if e.key == " ":
                capture_current_face()
            elif e.key == "Escape":
                exit_camera_mode(completed=False)

    page.on_keyboard_event = on_key_event

    async def camera_stream_loop():
        active_idx = cam_state["cam_idx"]
        cap = await asyncio.to_thread(open_camera_capture, active_idx)

        while cam_state["active"] and is_open[0]:
            if cam_state["cam_idx"] != active_idx:
                await asyncio.to_thread(cap.release)
                active_idx = cam_state["cam_idx"]
                cap = await asyncio.to_thread(open_camera_capture, active_idx)

            ret, frame = await asyncio.to_thread(cap.read)
            if ret and frame is not None and cam_state["scan_step"] < len(SCAN_ORDER):
                expected_face, _ = SCAN_ORDER[cam_state["scan_step"]]
                if not mini_cam["manual_orbit"]:  # <--- AQUÍ
                    target_yaw, target_pitch = FACE_3D_ANGLES[expected_face]
                    mini_cam["yaw"] += (target_yaw - mini_cam["yaw"]) * 0.35
                    mini_cam["pitch"] += (target_pitch - mini_cam["pitch"]) * 0.35

                b64_img, detected_9, patches_lab = await asyncio.to_thread(
                    process_camera_frame, frame, expected_face, cam_state["calibrated_labs"]
                )
                cam_state["latest_9"] = detected_9
                cam_state["latest_labs"] = patches_lab
                camera_preview.src = f"data:image/jpeg;base64,{b64_img}"
                render_mini_3d_guide(expected_face, detected_9, cam_state["scanned_faces"])
                if camera_panel.page:
                    camera_panel.update()

            await asyncio.sleep(0.065)

        await asyncio.to_thread(cap.release)

    async def start_camera_mode():
        is_animating[0] = False
        status_banner.value = "📷 Iniciando cámara de la Mac..."
        status_banner.color = ft.Colors.CYAN_ACCENT_200
        page.update()

        preferred = await asyncio.to_thread(find_mac_camera_index)
        cam_state["cam_idx"] = preferred
        cam_state["scan_step"] = 0
        cam_state["scanned_faces"] = {}
        cam_state["raw_labs"] = {}
        cam_state["calibrated_labs"] = dict(DEFAULT_LAB_REFS)
        cam_state["active"] = True
        first_face, first_prompt = SCAN_ORDER[0]
        mini_cam["yaw"], mini_cam["pitch"] = FACE_3D_ANGLES[first_face]
        mini_cam["manual_orbit"] = False  

        cam_switch_btn.text = f"Cámara ({preferred})"
        cube_view_panel.visible = False
        action_bar.visible = False
        camera_panel.visible = True
        update_playback_controls()

        _, first_prompt = SCAN_ORDER[0]
        status_banner.value = f"📷 {first_prompt}"
        page.update()

        page.run_task(camera_stream_loop)

    def on_camera_scan_click(e):
        if not is_turning[0]:
            page.run_task(start_camera_mode)

    def select_brush(color_code: str):
        def handler(e):
            selected_brush[0] = color_code
            for code, box in brush_boxes.items():
                box.border = ft.Border.all(
                    3.5 if code == color_code else 1.5,
                    ft.Colors.CYAN_ACCENT_200 if code == color_code else ft.Colors.WHITE_54,
                )
            status_banner.value = f"Color seleccionado: {FACE_NAMES[color_code]}"
            status_banner.color = ft.Colors.WHITE
            page.update()
        return handler

    def on_solve_click(e):
        is_animating[0] = False
        slice_anim["axis"] = None
        slice_anim["angle"] = 0.0
        raw_state = cube.to_kociemba_string()
        counts = {c: raw_state.count(c) for c in COLORS}
        if any(v != 9 for v in counts.values()):
            faltantes = ", ".join(f"{FACE_NAMES[k]}:{v}/9" for k, v in counts.items() if v != 9)
            status_banner.value = f"❌ Debe haber 9 cuadros por color ({faltantes})"
            status_banner.color = ft.Colors.RED_ACCENT_200
            page.update()
            return

        try:
            sol_str = kociemba.solve(raw_state)
            solution_steps.clear()
            if sol_str.strip():
                solution_steps.extend(sol_str.split())
            step_index[0] = 0

            if not solution_steps:
                status_banner.value = "✅ ¡El cubo ya está resuelto!"
                status_banner.color = ft.Colors.GREEN_ACCENT_400
                update_playback_controls()
                step_instruction.value = ""
                page.update()
            else:
                status_banner.value = f"✅ Resolviendo en {len(solution_steps)} movimientos..."
                status_banner.color = ft.Colors.GREEN_ACCENT_400
                page.run_task(animate_solution)
        except Exception:
            status_banner.value = "❌ Cubo imposible: revisa que no haya piezas repetidas."
            status_banner.color = ft.Colors.RED_ACCENT_200
            page.update()

    def on_reset(e):
        is_animating[0] = False
        slice_anim["axis"] = None
        slice_anim["angle"] = 0.0
        cube.reset()
        solution_steps.clear()
        step_index[0] = 0
        update_playback_controls()
        step_instruction.value = ""
        status_banner.value = "Cubo reiniciado. Arrastra para girar y pinta los cuadros."
        status_banner.color = ft.Colors.AMBER_300
        render_3d()

    def close_window(e):
        cam_state["active"] = False
        is_animating[0] = False
        is_open[0] = False
        if window_overlay in page.overlay:
            page.overlay.remove(window_overlay)
        page.update()

    sound_btn = ft.IconButton(
        icon=ft.Icons.VOLUME_UP,
        icon_color=ft.Colors.CYAN_ACCENT_200,
        tooltip="Silenciar / Activar efectos de sonido",
    )

    def toggle_sound(e):
        sound_enabled[0] = not sound_enabled[0]
        sound_btn.icon = ft.Icons.VOLUME_UP if sound_enabled[0] else ft.Icons.VOLUME_OFF
        sound_btn.icon_color = ft.Colors.CYAN_ACCENT_200 if sound_enabled[0] else ft.Colors.GREY_500
        page.update()

    sound_btn.on_click = toggle_sound

    for code in ["U", "R", "F", "D", "L", "B"]:
        is_selected = code == selected_brush[0]
        brush_boxes[code] = ft.Container(
            width=36,
            height=36,
            bgcolor=COLORS[code],
            border_radius=6,
            border=ft.Border.all(
                3.5 if is_selected else 1.5,
                ft.Colors.CYAN_ACCENT_200 if is_selected else ft.Colors.WHITE_54,
            ),
            on_click=select_brush(code),
            tooltip=FACE_NAMES[code],
        )

    brush_palette = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=12,
        controls=list(brush_boxes.values()),
    )

    title_bar = ft.Container(
        bgcolor=ft.Colors.GREY_900,
        padding=ft.Padding.symmetric(horizontal=18, vertical=8),
        border_radius=ft.BorderRadius.only(top_left=14, top_right=14),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.VIEW_IN_AR, color=ft.Colors.CYAN_ACCENT_200, size=22),
                        ft.Text(
                            "Solucionador Cubo de Rubik 3D",
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        sound_btn,
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.RED_700,
                            tooltip="Cerrar ventana",
                            on_click=close_window,
                        ),
                    ],
                ),
            ],
        ),
    )

    playback_bar = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=12,
        controls=[
            prev_step_btn,
            pause_resume_btn,
            next_step_btn,
        ],
    )

    action_bar = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=14,
        controls=[
            ft.OutlinedButton("Reiniciar", icon=ft.Icons.REFRESH, on_click=on_reset),
            ft.FilledTonalButton("Escanear Cámara", icon=ft.Icons.CAMERA_ALT, on_click=on_camera_scan_click),
            ft.FilledButton("Calcular Solución", icon=ft.Icons.AUTO_FIX_HIGH, on_click=on_solve_click),
        ],
    )

    cube_view_panel = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=6,
        controls=[
            ft.GestureDetector(
                on_pan_update=on_pan_cube,
                on_tap_up=on_tap_cube,
                content=canvas,
            ),
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                controls=[
                    ft.Text("Selecciona un color:", size=12, color=ft.Colors.WHITE_70),
                    brush_palette,
                ],
            ),
            step_instruction,
            playback_bar,
            speed_row,
        ],
    )

    desktop_window = ft.Container(
        width=820,
        height=690,
        bgcolor="#1E1E24",
        border_radius=14,
        border=ft.Border.all(1.5, ft.Colors.WHITE_24),
        shadow=ft.BoxShadow(blur_radius=28, color=ft.Colors.BLACK_87),
        content=ft.Column(
            spacing=0,
            controls=[
                title_bar,
                ft.Container(
                    expand=True,
                    padding=ft.Padding.symmetric(horizontal=24, vertical=8),
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                        controls=[
                            status_banner,
                            cube_view_panel,
                            camera_panel,
                            action_bar,
                        ],
                    ),
                ),
            ],
        ),
    )

    window_overlay = ft.Container(
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.65, ft.Colors.BLACK),
        alignment=ft.Alignment(0, 0),
        content=desktop_window,
    )

    page.overlay.append(window_overlay)
    render_3d()