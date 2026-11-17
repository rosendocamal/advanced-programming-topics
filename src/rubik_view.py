import asyncio, math, os, random, subprocess, sys, tempfile, wave
from pathlib import Path
import flet as ft
import flet.canvas as cv
import kociemba
import numpy as np

from camera_scanner import (
    DEFAULT_LAB_REFS,
    FACE_COLOR_NAMES,
    detect_available_cameras,
    open_camera_capture,
    process_camera_frame,
    reclassify_all_faces,
)

COLORS = {
    "U": "#FFFFFF",  # Up - Blanco
    "R": "#D50000",  # Right - Rojo
    "F": "#00C853",  # Front - Verde
    "D": "#FFD600",  # Down - Amarillo
    "L": "#FF6D00",  # Left - Naranja
    "B": "#2962FF",  # Back - Azul
}

FACE_NORMALS = {
    "U": (0.0, 1.0, 0.0),
    "D": (0.0, -1.0, 0.0),
    "F": (0.0, 0.0, 1.0),
    "B": (0.0, 0.0, -1.0),
    "R": (1.0, 0.0, 0.0),
    "L": (-1.0, 0.0, 0.0),
}

FACE_NAMES = {
    "U": "Blanco (Arriba)",
    "R": "Rojo (Derecha)",
    "F": "Verde (Frente)",
    "D": "Amarillo (Abajo)",
    "L": "Naranja (Izquierda)",
    "B": "Azul (Atrás)",
}

FACE_3D_ANGLES = {
    "F": (0.0, 0.22),
    "R": (-1.5708, 0.22),
    "B": (3.1416, 0.22),
    "L": (1.5708, 0.22),
    "U": (0.0, 1.48),
    "D": (0.0, -1.48),
}

MOVE_EXPLANATIONS = {
    "U": "Gira la cara SUPERIOR (Blanca) 90° en sentido horario",
    "U'": "Gira la cara SUPERIOR (Blanca) 90° en sentido antihorario",
    "U2": "Gira la cara SUPERIOR (Blanca) 180°",
    "D": "Gira la cara INFERIOR (Amarilla) 90° en sentido horario",
    "D'": "Gira la cara INFERIOR (Amarilla) 90° en sentido antihorario",
    "D2": "Gira la cara INFERIOR (Amarilla) 180°",
    "R": "Gira la cara DERECHA (Roja) 90° hacia arriba",
    "R'": "Gira la cara DERECHA (Roja) 90° hacia abajo",
    "R2": "Gira la cara DERECHA (Roja) 180°",
    "L": "Gira la cara IZQUIERDA (Naranja) 90° hacia abajo",
    "L'": "Gira la cara IZQUIERDA (Naranja) 90° hacia arriba",
    "L2": "Gira la cara IZQUIERDA (Naranja) 180°",
    "F": "Gira la cara FRONTAL (Verde) 90° en sentido horario",
    "F'": "Gira la cara FRONTAL (Verde) 90° en sentido antihorario",
    "F2": "Gira la cara FRONTAL (Verde) 180°",
    "B": "Gira la cara TRASERA (Azul) 90° en sentido horario",
    "B'": "Gira la cara TRASERA (Azul) 90° en sentido antihorario",
    "B2": "Gira la cara TRASERA (Azul) 180°",
}

ALL_STANDARD_MOVES = [
    "U", "U'", "U2",
    "D", "D'", "D2",
    "R", "R'", "R2",
    "L", "L'", "L2",
    "F", "F'", "F2",
    "B", "B'", "B2",
]

SPEED_PRESETS = [
    ("1x", 0.24, 0.30), ("2x", 0.12, 0.15), ("4x", 0.055, 0.07), ("0.5x", 0.85, 0.85),
]


def _ensure_sound_assets() -> tuple[Path, Path]:
    sound_dir = Path(tempfile.gettempdir()) / "rubik_sounds"
    sound_dir.mkdir(parents=True, exist_ok=True)
    click_wav = sound_dir / "turn_click.wav"
    win_wav = sound_dir / "victory.wav"

    if not click_wav.exists():
        sr = 22050
        dur = 0.045
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        env = np.exp(-t * 95.0)
        tone = 0.55 * np.sin(2 * np.pi * 620 * t) + 0.35 * np.sin(2 * np.pi * 1240 * t)
        pcm = (tone * env * 32767).astype(np.int16)
        with wave.open(str(click_wav), "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm.tobytes())

    if not win_wav.exists():
        sr = 22050
        notes = [523.25, 659.25, 783.99, 1046.50]
        chunks = []
        for idx, freq in enumerate(notes):
            dur = 0.11 if idx < 3 else 0.32
            t = np.linspace(0, dur, int(sr * dur), endpoint=False)
            env = np.exp(-t * (10.0 if idx < 3 else 5.5))
            wave_note = 0.45 * np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(2 * np.pi * freq * 2 * t)
            chunks.append((wave_note * env * 32767).astype(np.int16))
        pcm = np.concatenate(chunks)
        with wave.open(str(win_wav), "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm.tobytes())

    return click_wav, win_wav


def _play_wav_nonblocking(wav_path: Path):
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["afplay", str(wav_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform.startswith("linux") and not os.environ.get("ANDROID_ARGUMENT"):
            subprocess.Popen(["aplay", "-q", str(wav_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform == "win32":
            import winsound
            winsound.PlaySound(str(wav_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass


def play_turn_click(enabled: bool = True):
    if enabled:
        click_wav, _ = _ensure_sound_assets()
        _play_wav_nonblocking(click_wav)


def play_victory_sound(enabled: bool = True):
    if enabled:
        _, win_wav = _ensure_sound_assets()
        _play_wav_nonblocking(win_wav)


class RubikCubeState:
    """Modelo lógico del Cubo de Rubik 3x3 compatible con Kociemba (URFDLB)."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.faces = {face: [face] * 9 for face in ["U", "R", "F", "D", "L", "B"]}

    def copy_from(self, other: "RubikCubeState"):
        self.faces = {k: list(v) for k, v in other.faces.items()}

    def to_kociemba_string(self) -> str:
        return "".join("".join(self.faces[f]) for f in ["U", "R", "F", "D", "L", "B"])

    def color_counts(self) -> dict[str, int]:
        counts = {c: 0 for c in ["U", "R", "F", "D", "L", "B"]}
        for stickers in self.faces.values():
            for s in stickers:
                if s in counts:
                    counts[s] += 1
        return counts

    def is_color_count_valid(self) -> bool:
        return all(count == 9 for count in self.color_counts().values())

    def _rotate_face_cw(self, face: str):
        f = self.faces[face]
        self.faces[face] = [f[6], f[3], f[0], f[7], f[4], f[1], f[8], f[5], f[2]]

    def move_once(self, base: str):
        self._rotate_face_cw(base)
        f = self.faces
        if base == "U":
            temp = [f["F"][0], f["F"][1], f["F"][2]]
            f["F"][0], f["F"][1], f["F"][2] = f["R"][0], f["R"][1], f["R"][2]
            f["R"][0], f["R"][1], f["R"][2] = f["B"][0], f["B"][1], f["B"][2]
            f["B"][0], f["B"][1], f["B"][2] = f["L"][0], f["L"][1], f["L"][2]
            f["L"][0], f["L"][1], f["L"][2] = temp
        elif base == "D":
            temp = [f["F"][6], f["F"][7], f["F"][8]]
            f["F"][6], f["F"][7], f["F"][8] = f["L"][6], f["L"][7], f["L"][8]
            f["L"][6], f["L"][7], f["L"][8] = f["B"][6], f["B"][7], f["B"][8]
            f["B"][6], f["B"][7], f["B"][8] = f["R"][6], f["R"][7], f["R"][8]
            f["R"][6], f["R"][7], f["R"][8] = temp
        elif base == "R":
            temp = [f["U"][2], f["U"][5], f["U"][8]]
            f["U"][2], f["U"][5], f["U"][8] = f["F"][2], f["F"][5], f["F"][8]
            f["F"][2], f["F"][5], f["F"][8] = f["D"][2], f["D"][5], f["D"][8]
            f["D"][2], f["D"][5], f["D"][8] = f["B"][6], f["B"][3], f["B"][0]
            f["B"][6], f["B"][3], f["B"][0] = temp
        elif base == "L":
            temp = [f["U"][0], f["U"][3], f["U"][6]]
            f["U"][0], f["U"][3], f["U"][6] = f["B"][8], f["B"][5], f["B"][2]
            f["B"][8], f["B"][5], f["B"][2] = f["D"][0], f["D"][3], f["D"][6]
            f["D"][0], f["D"][3], f["D"][6] = f["F"][0], f["F"][3], f["F"][6]
            f["F"][0], f["F"][3], f["F"][6] = temp
        elif base == "F":
            temp = [f["U"][6], f["U"][7], f["U"][8]]
            f["U"][6], f["U"][7], f["U"][8] = f["L"][8], f["L"][5], f["L"][2]
            f["L"][8], f["L"][5], f["L"][2] = f["D"][2], f["D"][1], f["D"][0]
            f["D"][2], f["D"][1], f["D"][0] = f["R"][0], f["R"][3], f["R"][6]
            f["R"][0], f["R"][3], f["R"][6] = temp
        elif base == "B":
            temp = [f["U"][0], f["U"][1], f["U"][2]]
            f["U"][0], f["U"][1], f["U"][2] = f["R"][2], f["R"][5], f["R"][8]
            f["R"][2], f["R"][5], f["R"][8] = f["D"][8], f["D"][7], f["D"][6]
            f["D"][8], f["D"][7], f["D"][6] = f["L"][6], f["L"][3], f["L"][0]
            f["L"][6], f["L"][3], f["L"][0] = temp

    def apply_move(self, move: str):
        base = move[0]
        turns = 3 if move.endswith("'") else (2 if move.endswith("2") else 1)
        for _ in range(turns):
            self.move_once(base)

    @staticmethod
    def invert_move(move: str) -> str:
        if move.endswith("'"):
            return move[0]
        if move.endswith("2"):
            return move
        return move + "'"


def _rot_x(p: tuple[float, float, float], a: float) -> tuple[float, float, float]:
    x, y, z = p
    c, s = math.cos(a), math.sin(a)
    return (x, y * c - z * s, y * s + z * c)


def _rot_y(p: tuple[float, float, float], a: float) -> tuple[float, float, float]:
    x, y, z = p
    c, s = math.cos(a), math.sin(a)
    return (x * c + z * s, y, -x * s + z * c)


def _rot_z(p: tuple[float, float, float], a: float) -> tuple[float, float, float]:
    x, y, z = p
    c, s = math.cos(a), math.sin(a)
    return (x * c - y * s, x * s + y * c, z)


def _mat_mul(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    return [
        [sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)]
        for i in range(3)
    ]


def _mat_vec(M: list[list[float]], p: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        M[0][0] * p[0] + M[0][1] * p[1] + M[0][2] * p[2],
        M[1][0] * p[0] + M[1][1] * p[1] + M[1][2] * p[2],
        M[2][0] * p[0] + M[2][1] * p[1] + M[2][2] * p[2],
    )


def _rot_x_mat(a: float) -> list[list[float]]:
    c, s = math.cos(a), math.sin(a)
    return [[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]]


def _rot_y_mat(a: float) -> list[list[float]]:
    c, s = math.cos(a), math.sin(a)
    return [[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]]


def _make_cam_mat(yaw: float, pitch: float) -> list[list[float]]:
    return _mat_mul(_rot_x_mat(-pitch), _rot_y_mat(yaw))


def _rotate_slice_vector(p: tuple[float, float, float], base: str, angle: float) -> tuple[float, float, float]:
    if base == "R":
        return _rot_x(p, -angle)
    if base == "L":
        return _rot_x(p, angle)
    if base == "U":
        return _rot_y(p, -angle)
    if base == "D":
        return _rot_y(p, angle)
    if base == "F":
        return _rot_z(p, -angle)
    if base == "B":
        return _rot_z(p, angle)
    return p


def _sticker_cubie_coords(face: str, idx: int) -> tuple[int, int, int]:
    row, col = divmod(idx, 3)
    if face == "F":
        return (col - 1, 1 - row, 1)
    if face == "B":
        return (1 - col, 1 - row, -1)
    if face == "U":
        return (col - 1, 1, row - 1)
    if face == "D":
        return (col - 1, -1, 1 - row)
    if face == "R":
        return (1, 1 - row, 1 - col)
    if face == "L":
        return (-1, 1 - row, col - 1)
    return (0, 0, 0)


def _is_cubie_in_slice(cx: int, cy: int, cz: int, base: str) -> bool:
    return (
        (base == "R" and cx == 1)
        or (base == "L" and cx == -1)
        or (base == "U" and cy == 1)
        or (base == "D" and cy == -1)
        or (base == "F" and cz == 1)
        or (base == "B" and cz == -1)
    )


def _transform_to_camera_space(
    p: tuple[float, float, float],
    cam_rot: list[list[float]],
) -> tuple[float, float, float]:
    return _mat_vec(cam_rot, p)


def _project_camera_point(
    cam_pt: tuple[float, float, float],
    cx: float,
    cy: float,
    scale: float,
) -> tuple[float, float, float]:
    x, y, z = cam_pt
    cam_dist = 8.4
    factor = (scale * 5.3) / (cam_dist - z)
    return (cx + x * factor, cy - y * factor, z)


def _is_normal_facing_camera(
    cam_normal: tuple[float, float, float],
    cam_pts: list[tuple[float, float, float]],
) -> bool:
    nx, ny, nz = cam_normal
    mx = sum(p[0] for p in cam_pts) * 0.25
    my = sum(p[1] for p in cam_pts) * 0.25
    mz = sum(p[2] for p in cam_pts) * 0.25
    dot = nx * (-mx) + ny * (-my) + nz * (8.4 - mz)
    return dot > 0.01


def _shade_hex_color(hex_color: str, cam_normal: tuple[float, float, float]) -> str:
    nx, ny, nz = cam_normal
    lx, ly, lz = -0.35, 0.72, 0.60
    l_len = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / l_len, ly / l_len, lz / l_len

    ndotl = max(-1.0, min(1.0, nx * lx + ny * ly + nz * lz))
    factor = 0.85 + 0.15 * ((ndotl + 1.0) * 0.5)

    h = hex_color.lstrip("#")
    r = min(255, int(int(h[0:2], 16) * factor))
    g = min(255, int(int(h[2:4], 16) * factor))
    b = min(255, int(int(h[4:6], 16) * factor))
    return f"#{r:02X}{g:02X}{b:02X}"


def _point_in_polygon(px: float, py: float, poly: list[tuple[float, float]]) -> bool:
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / ((yj - yi) + 1e-9) + xi):
            inside = not inside
        j = i
    return inside


def _get_sticker_3d_quad(face: str, idx: int, pad: float = 0.05) -> list[tuple[float, float, float]]:
    row, col = divmod(idx, 3)
    step = 2.0 / 3.0
    u0 = -1.0 + col * step + pad
    u1 = -1.0 + (col + 1) * step - pad
    v0 = 1.0 - (row + 1) * step + pad
    v1 = 1.0 - row * step - pad

    if face == "F":
        return [(u0, v1, 1.0), (u1, v1, 1.0), (u1, v0, 1.0), (u0, v0, 1.0)]
    if face == "B":
        return [(-u0, v1, -1.0), (-u1, v1, -1.0), (-u1, v0, -1.0), (-u0, v0, -1.0)]
    if face == "U":
        return [(u0, 1.0, -v1), (u1, 1.0, -v1), (u1, 1.0, -v0), (u0, 1.0, -v0)]
    if face == "D":
        return [(u0, -1.0, v1), (u1, -1.0, v1), (u1, -1.0, v0), (u0, -1.0, v0)]
    if face == "R":
        return [(1.0, v1, -u0), (1.0, v1, -u1), (1.0, v0, -u1), (1.0, v0, -u0)]
    if face == "L":
        return [(-1.0, v1, u0), (-1.0, v1, u1), (-1.0, v0, u1), (-1.0, v0, u0)]
    return []


def _get_cubie_black_faces(cx: int, cy: int, cz: int) -> list[tuple[str, list[tuple[float, float, float]]]]:
    s = 2.0 / 3.0
    x0, x1 = cx * s - s / 2, cx * s + s / 2
    y0, y1 = cy * s - s / 2, cy * s + s / 2
    z0, z1 = cz * s - s / 2, cz * s + s / 2
    return [
        ("F", [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)]),
        ("B", [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)]),
        ("U", [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]),
        ("D", [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)]),
        ("R", [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)]),
        ("L", [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)]),
    ]


def _resolve_physical_swipe_move(
    face: str,
    idx: int,
    dx: float,
    dy: float,
    cam_rot: list[list[float]],
) -> str | None:
    cx, cy, cz = _sticker_cubie_coords(face, idx)

    tangent_axes = {
        "F": [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
        "B": [(-1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
        "U": [(1.0, 0.0, 0.0), (0.0, 0.0, 1.0)],
        "D": [(1.0, 0.0, 0.0), (0.0, 0.0, -1.0)],
        "R": [(0.0, 0.0, -1.0), (0.0, 1.0, 0.0)],
        "L": [(0.0, 0.0, 1.0), (0.0, 1.0, 0.0)],
    }

    p0_cam = _transform_to_camera_space((0.0, 0.0, 0.0), cam_rot)
    s0_x, s0_y, _ = _project_camera_point(p0_cam, 0.0, 0.0, 100.0)

    best_axis = None
    best_sign = 1.0
    best_score = 0.0

    for axis in tangent_axes[face]:
        p1_cam = _transform_to_camera_space(axis, cam_rot)
        s1_x, s1_y, _ = _project_camera_point(p1_cam, 0.0, 0.0, 100.0)
        vx, vy = s1_x - s0_x, s1_y - s0_y
        v_len = math.hypot(vx, vy) + 1e-9
        vx /= v_len
        vy /= v_len
        proj = dx * vx + dy * vy
        if abs(proj) > best_score:
            best_score = abs(proj)
            best_axis = axis
            best_sign = 1.0 if proj >= 0 else -1.0

    if best_axis is None:
        return None

    nx, ny, nz = FACE_NORMALS[face]
    mx, my, mz = best_axis[0] * best_sign, best_axis[1] * best_sign, best_axis[2] * best_sign

    rx = ny * mz - nz * my
    ry = nz * mx - nx * mz
    rz = nx * my - ny * mx

    if abs(rx) > 0.5:
        if cx == 1:
            return "R" if rx < 0 else "R'"
        if cx == -1:
            return "L" if rx > 0 else "L'"
    elif abs(ry) > 0.5:
        if cy == 1:
            return "U" if ry < 0 else "U'"
        if cy == -1:
            return "D" if ry > 0 else "D'"
    elif abs(rz) > 0.5:
        if cz == 1:
            return "F" if rz < 0 else "F'"
        if cz == -1:
            return "B" if rz > 0 else "B'"

    face_center_3d = (nx, ny, nz)
    fc_cam = _transform_to_camera_space(face_center_3d, cam_rot)
    fc_x, fc_y, _ = _project_camera_point(fc_cam, 0.0, 0.0, 100.0)

    quad_3d = _get_sticker_3d_quad(face, idx, pad=0.05)
    st_3d = (
        sum(p[0] for p in quad_3d) * 0.25,
        sum(p[1] for p in quad_3d) * 0.25,
        sum(p[2] for p in quad_3d) * 0.25,
    )
    st_cam = _transform_to_camera_space(st_3d, cam_rot)
    st_x, st_y, _ = _project_camera_point(st_cam, 0.0, 0.0, 100.0)

    rad_x = st_x - fc_x
    rad_y = st_y - fc_y
    if math.hypot(rad_x, rad_y) > 2.0:
        cross_2d = rad_x * dy - rad_y * dx
        return face if cross_2d >= 0 else f"{face}'"

    return face if (dx + dy) >= 0 else f"{face}'"


def open_rubik_interface(page: ft.Page):
    cube = RubikCubeState()
    selected_brush: list[str | None] = [None]
    solution_steps: list[str] = []
    step_index = [0]
    is_animating = [False]
    is_turning = [False]
    is_open = [True]
    sound_enabled = [True]
    manual_solve_mode = [False]
    hide_palette_after_scan = [False]
    speed_idx = [0]  # 0: 1x, 1: 2x, 2: 4x, 3: 0.5x
    active_turn = {"base": None, "angle": 0.0}

    cam_state = {
        "active": False,
        "available_cams": [0],
        "cam_pos": 0,
        "cam_idx": 0,
        "scanned_faces": {},
        "capture_history": [],
        "raw_labs": {},
        "calibrated_labs": dict(DEFAULT_LAB_REFS),
        "latest_9": ["U"] * 9,
        "latest_labs": [],
        "detected_center": "F",
        "center_valid": True,
    }

    # Matriz de rotación libre 360° (permite voltear el cubo completamente boca abajo)
    cam_rot = [_make_cam_mat(-0.62, 0.44)]
    drag_state = {
        "start_x": 0.0,
        "start_y": 0.0,
        "origin_x": 0.0,
        "origin_y": 0.0,
        "hit_sticker": None,
        "swipe_triggered": False,
    }
    rendered_polygons: list[tuple[float, str, int, list[tuple[float, float]]]] = []

    mini_rot = [_make_cam_mat(0.0, 0.22)]
    mini_manual_orbit = [False]
    mini_drag = {"start_x": 0.0, "start_y": 0.0}

    status_banner = ft.Text(
        "Elige un color de la paleta para pintar, o usa 'Armar Manualmente' / 'Escanear Cámara'.",
        size=13,
        color="#80DEEA",
        text_align=ft.TextAlign.CENTER,
    )

    step_instruction = ft.Text(
        "Estado inicial: Cubo resuelto (9/9 en cada color)",
        size=15,
        weight=ft.FontWeight.BOLD,
        color="#FFFFFF",
        text_align=ft.TextAlign.CENTER,
    )

    progress_text = ft.Text("Paso 0 / 0", size=12, color="#9E9E9E")

    def build_sticker_shapes(
        cube_faces: dict[str, list[str]],
        rot_mat: list[list[float]],
        cx: float,
        cy: float,
        scale: float,
        turn_base: str | None = None,
        turn_angle: float = 0.0,
        record_hitboxes: bool = False,
        draw_center_dots: bool = True,
    ) -> list:
        body_list: list[tuple[float, list[tuple[float, float]], str]] = []
        sticker_list: list[tuple[float, str, int, list[tuple[float, float]], str]] = []

        if turn_base is not None:
            for bx in (-1, 0, 1):
                for by in (-1, 0, 1):
                    for bz in (-1, 0, 1):
                        if bx == 0 and by == 0 and bz == 0:
                            continue
                        in_slice = _is_cubie_in_slice(bx, by, bz, turn_base)
                        for f_dir, bquad in _get_cubie_black_faces(bx, by, bz):
                            n_vec = FACE_NORMALS[f_dir]
                            if in_slice:
                                pts_3d = [_rotate_slice_vector(pt, turn_base, turn_angle) for pt in bquad]
                                n_vec = _rotate_slice_vector(n_vec, turn_base, turn_angle)
                            else:
                                pts_3d = bquad
                            cam_pts = [_transform_to_camera_space(pt, rot_mat) for pt in pts_3d]
                            cam_norm = _transform_to_camera_space(n_vec, rot_mat)
                            if _is_normal_facing_camera(cam_norm, cam_pts):
                                proj = [_project_camera_point(cp, cx, cy, scale) for cp in cam_pts]
                                avg_z = sum(p[2] for p in proj) / 4.0
                                poly_2d = [(p[0], p[1]) for p in proj]
                                body_list.append((avg_z, poly_2d, "#14141A"))
        else:
            hull_faces = [
                ("F", [(-1.0, 1.0, 1.0), (1.0, 1.0, 1.0), (1.0, -1.0, 1.0), (-1.0, -1.0, 1.0)]),
                ("B", [(1.0, 1.0, -1.0), (-1.0, 1.0, -1.0), (-1.0, -1.0, -1.0), (1.0, -1.0, -1.0)]),
                ("U", [(-1.0, 1.0, -1.0), (1.0, 1.0, -1.0), (1.0, 1.0, 1.0), (-1.0, 1.0, 1.0)]),
                ("D", [(-1.0, -1.0, 1.0), (1.0, -1.0, 1.0), (1.0, -1.0, -1.0), (-1.0, -1.0, -1.0)]),
                ("R", [(1.0, 1.0, 1.0), (1.0, 1.0, -1.0), (1.0, -1.0, -1.0), (1.0, -1.0, 1.0)]),
                ("L", [(-1.0, 1.0, -1.0), (-1.0, 1.0, 1.0), (-1.0, -1.0, 1.0), (-1.0, -1.0, -1.0)]),
            ]
            for f_dir, hquad in hull_faces:
                cam_pts = [_transform_to_camera_space(pt, rot_mat) for pt in hquad]
                cam_norm = _transform_to_camera_space(FACE_NORMALS[f_dir], rot_mat)
                if _is_normal_facing_camera(cam_norm, cam_pts):
                    proj = [_project_camera_point(cp, cx, cy, scale) for cp in cam_pts]
                    avg_z = sum(p[2] for p in proj) / 4.0
                    poly_2d = [(p[0], p[1]) for p in proj]
                    body_list.append((avg_z, poly_2d, "#14141A"))

        for face in ["U", "R", "F", "D", "L", "B"]:
            for idx in range(9):
                quad_3d = _get_sticker_3d_quad(face, idx, pad=0.05)
                n_vec = FACE_NORMALS[face]
                if turn_base is not None:
                    scx, scy, scz = _sticker_cubie_coords(face, idx)
                    if _is_cubie_in_slice(scx, scy, scz, turn_base):
                        quad_3d = [_rotate_slice_vector(pt, turn_base, turn_angle) for pt in quad_3d]
                        n_vec = _rotate_slice_vector(n_vec, turn_base, turn_angle)

                cam_pts = [_transform_to_camera_space(pt, rot_mat) for pt in quad_3d]
                cam_norm = _transform_to_camera_space(n_vec, rot_mat)
                if _is_normal_facing_camera(cam_norm, cam_pts):
                    proj = [_project_camera_point(cp, cx, cy, scale) for cp in cam_pts]
                    avg_z = sum(p[2] for p in proj) / 4.0
                    poly_2d = [(p[0], p[1]) for p in proj]
                    shaded_hex = _shade_hex_color(COLORS[cube_faces[face][idx]], cam_norm)
                    sticker_list.append((avg_z, face, idx, poly_2d, shaded_hex))

        body_list.sort(key=lambda item: item[0])
        sticker_list.sort(key=lambda item: item[0])

        if record_hitboxes:
            rendered_polygons.clear()

        shapes = []
        for _, poly_2d, fill_hex in body_list:
            shapes.append(
                cv.Path(
                    elements=[
                        cv.Path.MoveTo(poly_2d[0][0], poly_2d[0][1]),
                        cv.Path.LineTo(poly_2d[1][0], poly_2d[1][1]),
                        cv.Path.LineTo(poly_2d[2][0], poly_2d[2][1]),
                        cv.Path.LineTo(poly_2d[3][0], poly_2d[3][1]),
                        cv.Path.Close(),
                    ],
                    paint=ft.Paint(color=fill_hex, style=ft.PaintingStyle.FILL),
                )
            )

        for avg_z, face, idx, poly_2d, fill_hex in sticker_list:
            if record_hitboxes:
                rendered_polygons.append((avg_z, face, idx, poly_2d))

            shapes.append(
                cv.Path(
                    elements=[
                        cv.Path.MoveTo(poly_2d[0][0], poly_2d[0][1]),
                        cv.Path.LineTo(poly_2d[1][0], poly_2d[1][1]),
                        cv.Path.LineTo(poly_2d[2][0], poly_2d[2][1]),
                        cv.Path.LineTo(poly_2d[3][0], poly_2d[3][1]),
                        cv.Path.Close(),
                    ],
                    paint=ft.Paint(color=fill_hex, style=ft.PaintingStyle.FILL),
                )
            )
            shapes.append(
                cv.Path(
                    elements=[
                        cv.Path.MoveTo(poly_2d[0][0], poly_2d[0][1]),
                        cv.Path.LineTo(poly_2d[1][0], poly_2d[1][1]),
                        cv.Path.LineTo(poly_2d[2][0], poly_2d[2][1]),
                        cv.Path.LineTo(poly_2d[3][0], poly_2d[3][1]),
                        cv.Path.Close(),
                    ],
                    paint=ft.Paint(color="#101015", style=ft.PaintingStyle.STROKE, stroke_width=1.6),
                )
            )
            if draw_center_dots and idx == 4:
                mx = sum(p[0] for p in poly_2d) / 4.0
                my = sum(p[1] for p in poly_2d) / 4.0
                shapes.append(
                    cv.Circle(
                        x=mx,
                        y=my,
                        radius=3.0,
                        paint=ft.Paint(color="#1C1C22", style=ft.PaintingStyle.FILL),
                    )
                )

        return shapes

    cube_canvas = cv.Canvas(width=380, height=330, shapes=[])
    mini_cube_canvas = cv.Canvas(width=215, height=215, shapes=[])

    solve_btn = ft.FilledButton(
        "Calcular Solución",
        icon=ft.Icons.AUTO_FIX_HIGH,
        style=ft.ButtonStyle(bgcolor="#00C853", color="#000000"),
    )

    def render_3d_cube():
        cube_canvas.shapes = build_sticker_shapes(
            cube_faces=cube.faces,
            rot_mat=cam_rot[0],
            cx=190.0,
            cy=165.0,
            scale=122.0,
            turn_base=active_turn["base"],
            turn_angle=active_turn["angle"],
            record_hitboxes=(active_turn["base"] is None),
            draw_center_dots=True,
        )

    def render_mini_3d_guide(active_face: str, live_9: list[str], scanned_faces: dict[str, list[str]]):
        preview_faces = {f: ["D"] * 9 for f in ["U", "R", "F", "D", "L", "B"]}
        for f_code in ["U", "R", "F", "D", "L", "B"]:
            if f_code == active_face:
                preview_faces[f_code] = list(live_9)
            elif f_code in scanned_faces:
                preview_faces[f_code] = list(scanned_faces[f_code])
            else:
                preview_faces[f_code] = [f_code if i == 4 else "U" for i in range(9)]

        mini_cube_canvas.shapes = build_sticker_shapes(
            cube_faces=preview_faces,
            rot_mat=mini_rot[0],
            cx=107.5,
            cy=107.5,
            scale=72.0,
            record_hitboxes=False,
            draw_center_dots=True,
        )

    def on_mini_pan_start(e: ft.DragStartEvent):
        mini_drag["start_x"] = e.local_position.x
        mini_drag["start_y"] = e.local_position.y
        mini_manual_orbit[0] = True

    def on_mini_pan_update(e: ft.DragUpdateEvent):
        dx = e.local_position.x - mini_drag["start_x"]
        dy = e.local_position.y - mini_drag["start_y"]
        mini_drag["start_x"] = e.local_position.x
        mini_drag["start_y"] = e.local_position.y
        rot_y = _rot_y_mat(dx * 0.016)
        rot_x = _rot_x_mat(dy * 0.016)
        mini_rot[0] = _mat_mul(rot_x, _mat_mul(rot_y, mini_rot[0]))
        render_mini_3d_guide(
            cam_state.get("detected_center", "F"),
            cam_state["latest_9"],
            cam_state["scanned_faces"],
        )
        if mini_cube_canvas.page:
            mini_cube_canvas.update()

    def _find_sticker_at(px: float, py: float) -> tuple[str, int] | None:
        for _, face, idx, poly in reversed(rendered_polygons):
            if _point_in_polygon(px, py, poly):
                return (face, idx)
        return None

    def on_pan_start(e: ft.DragStartEvent):
        px, py = e.local_position.x, e.local_position.y
        drag_state["start_x"] = px
        drag_state["start_y"] = py
        drag_state["origin_x"] = px
        drag_state["origin_y"] = py
        drag_state["hit_sticker"] = _find_sticker_at(px, py)
        drag_state["swipe_triggered"] = False

    def on_pan_update(e: ft.DragUpdateEvent):
        px, py = e.local_position.x, e.local_position.y
        dx = px - drag_state["start_x"]
        dy = py - drag_state["start_y"]
        drag_state["start_x"] = px
        drag_state["start_y"] = py

        if manual_solve_mode[0] and drag_state["hit_sticker"] is not None:
            if drag_state["swipe_triggered"] or is_turning[0]:
                return
            total_dx = px - drag_state["origin_x"]
            total_dy = py - drag_state["origin_y"]
            if math.hypot(total_dx, total_dy) >= 18.0:
                drag_state["swipe_triggered"] = True
                face, idx = drag_state["hit_sticker"]
                move = _resolve_physical_swipe_move(face, idx, total_dx, total_dy, cam_rot[0])
                if move:
                    trigger_manual_move(move)
            return

        # Rotación 3D libre 360° en pantalla (permite subir el amarillo y bajar el blanco)
        rot_y = _rot_y_mat(dx * 0.013)
        rot_x = _rot_x_mat(dy * 0.013)
        cam_rot[0] = _mat_mul(rot_x, _mat_mul(rot_y, cam_rot[0]))
        render_3d_cube()
        cube_canvas.update()

    def on_tap_down(e: ft.TapEvent):
        if manual_solve_mode[0] or is_animating[0] or is_turning[0] or cam_state["active"]:
            return
        if hide_palette_after_scan[0]:
            return

        hit = _find_sticker_at(e.local_position.x, e.local_position.y)
        if hit is not None:
            if selected_brush[0] is None:
                status_banner.value = "👆 Primero selecciona un color de la paleta inferior para pintar pegatinas."
                status_banner.color = "#FFD54F"
                page.update()
                return

            face, idx = hit
            if idx == 4:
                status_banner.value = (
                    f"El centro de la cara {FACE_NAMES[face]} es fijo y define el color de esa cara."
                )
                status_banner.color = "#FFD54F"
            else:
                cube.faces[face][idx] = selected_brush[0]
                solution_steps.clear()
                step_index[0] = 0
                update_playback_controls()
                update_brush_ui()
                render_3d_cube()
                if cube.is_color_count_valid():
                    status_banner.value = "✓ Conteo completo (9/9 en cada color). Ya puedes calcular la solución."
                    status_banner.color = "#00E676"
                else:
                    counts = cube.color_counts()
                    invalid = ", ".join(
                        f"{FACE_COLOR_NAMES[c]} ({counts[c]}/9)"
                        for c in ["U", "R", "F", "D", "L", "B"]
                        if counts[c] != 9
                    )
                    status_banner.value = f"Pegatina actualizada. Ajusta los conteos para resolver: {invalid}"
                    status_banner.color = "#80DEEA"
            page.update()

    interactive_cube = ft.GestureDetector(
        content=cube_canvas,
        on_pan_start=on_pan_start,
        on_pan_update=on_pan_update,
        on_tap_down=on_tap_down,
        drag_interval=16,
    )

    interactive_mini_cube = ft.GestureDetector(
        content=mini_cube_canvas,
        on_pan_start=on_mini_pan_start,
        on_pan_update=on_mini_pan_update,
        drag_interval=16,
    )

    brush_buttons: dict[str, ft.Container] = {}
    brush_count_labels: dict[str, ft.Text] = {}

    def select_brush(color_code: str):
        selected_brush[0] = color_code
        update_brush_ui()
        status_banner.value = (
            f"Pincel activo: {FACE_NAMES[color_code]} — Haz clic en una pegatina lateral o esquina para pintarla."
        )
        status_banner.color = "#80DEEA"
        page.update()

    def update_brush_ui():
        counts = cube.color_counts()
        all_valid = True
        for code, btn in brush_buttons.items():
            is_sel = selected_brush[0] is not None and code == selected_brush[0]
            btn.border = ft.Border.all(3 if is_sel else 1, "#00E5FF" if is_sel else "#616161")
            btn.scale = 1.08 if is_sel else 1.0

            cnt = counts[code]
            lbl = brush_count_labels[code]
            lbl.value = f"{cnt}/9"
            if cnt == 9:
                lbl.color = "#00E676"
            else:
                all_valid = False
                lbl.color = "#FF5252" if cnt > 9 else "#FFD54F"

        solve_btn.disabled = (not all_valid) or cam_state["active"]
        solve_btn.tooltip = (
            "Calcular pasos para resolver el cubo"
            if all_valid
            else "Cada uno de los 6 colores debe tener exactamente 9 pegatinas (9/9)"
        )

    for code in ["U", "R", "F", "D", "L", "B"]:
        count_txt = ft.Text("9/9", size=10, weight=ft.FontWeight.BOLD, color="#00E676")
        brush_count_labels[code] = count_txt
        swatch = ft.Container(
            width=32,
            height=32,
            bgcolor=COLORS[code],
            border_radius=7,
            tooltip=f"Pincel: {FACE_NAMES[code]}",
            on_click=lambda e, c=code: select_brush(c),
        )
        brush_buttons[code] = swatch

    brush_palette = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=12,
        controls=[
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                controls=[brush_buttons[code], brush_count_labels[code]],
            )
            for code in ["U", "R", "F", "D", "L", "B"]
        ],
    )

    brush_section = ft.Column(
        visible=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
        controls=[
            ft.Text(
                "Pincel de pegatinas (los centros con punto son fijos):",
                size=12,
                color="#B3FFFFFF",
            ),
            brush_palette,
        ],
    )

    prev_btn = ft.OutlinedButton("Anterior", icon=ft.Icons.SKIP_PREVIOUS, disabled=True)
    play_btn = ft.FilledButton(
        "Reproducir",
        icon=ft.Icons.PLAY_ARROW,
        disabled=True,
        style=ft.ButtonStyle(bgcolor="#2979FF", color="#FFFFFF"),
    )
    next_btn = ft.OutlinedButton("Siguiente", icon=ft.Icons.SKIP_NEXT, disabled=True)

    speed_label_text = ft.Text("x1", size=12, weight=ft.FontWeight.BOLD, color="#00E5FF")
    speed_btn = ft.Container(
        bgcolor="#2A2A36",
        border=ft.Border.all(1, "#00E5FF"),
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        tooltip="Velocidad de giro: x1 → x2 → x4 → x0.5",
        content=ft.Row(
            tight=True,
            spacing=4,
            controls=[
                ft.Icon(ft.Icons.SPEED, size=15, color="#00E5FF"),
                speed_label_text,
            ],
        ),
    )

    def on_speed_click(e):
        speed_idx[0] = (speed_idx[0] + 1) % len(SPEED_PRESETS)
        preset_name = SPEED_PRESETS[speed_idx[0]][0]
        display_tag = f"x{preset_name.rstrip('x')}"
        speed_label_text.value = display_tag
        status_banner.value = f"⚡ Velocidad de giro ajustada a {display_tag}"
        status_banner.color = "#80DEEA"
        page.update()

    speed_btn.on_click = on_speed_click

    def update_playback_controls():
        total = len(solution_steps)
        idx = step_index[0]
        progress_text.value = f"Paso {idx} / {total}"
        prev_btn.disabled = idx <= 0 or is_animating[0] or is_turning[0] or cam_state["active"]
        next_btn.disabled = idx >= total or is_animating[0] or is_turning[0] or cam_state["active"]
        play_btn.disabled = total == 0 or idx >= total or is_turning[0] or cam_state["active"]
        play_btn.text = "Pausar" if is_animating[0] else "Reproducir"
        play_btn.icon = ft.Icons.PAUSE if is_animating[0] else ft.Icons.PLAY_ARROW

    async def animate_physical_turn(move: str, duration: float | None = None):
        if duration is None:
            duration = SPEED_PRESETS[speed_idx[0]][1]
        base = move[0]
        if move.endswith("'"):
            target_angle = -math.pi / 2
        elif move.endswith("2"):
            target_angle = math.pi
        else:
            target_angle = math.pi / 2

        is_turning[0] = True
        active_turn["base"] = base
        play_turn_click(sound_enabled[0])
        frames = 18 if duration >= 0.60 else (10 if duration >= 0.16 else (7 if duration >= 0.09 else 4))
        for i in range(1, frames + 1):
            if not is_open[0]:
                break
            t = i / frames
            eased = 1 - (1 - t) ** 3
            active_turn["angle"] = target_angle * eased
            render_3d_cube()
            cube_canvas.update()
            await asyncio.sleep(duration / frames)

        active_turn["base"] = None
        active_turn["angle"] = 0.0
        cube.apply_move(move)
        is_turning[0] = False
        render_3d_cube()
        cube_canvas.update()

    async def step_forward_task():
        if step_index[0] < len(solution_steps) and not is_turning[0]:
            move = solution_steps[step_index[0]]
            step_index[0] += 1
            step_instruction.value = f"Paso {step_index[0]}: {move}  →  {MOVE_EXPLANATIONS[move]}"
            update_playback_controls()
            page.update()

            await animate_physical_turn(move)

            if step_index[0] >= len(solution_steps):
                step_instruction.value = "🎉 ¡Cubo Resuelto!"
                status_banner.value = "¡Listo! Todos los pasos han sido completados."
                status_banner.color = "#00E676"
                play_victory_sound(sound_enabled[0])
            update_playback_controls()
            page.update()

    async def step_backward_task():
        if step_index[0] > 0 and not is_turning[0]:
            step_index[0] -= 1
            move = solution_steps[step_index[0]]
            inv_move = RubikCubeState.invert_move(move)
            step_instruction.value = (
                f"Retrocediendo paso {step_index[0] + 1}: {move}"
                if step_index[0] > 0
                else "Listo para iniciar la solución."
            )
            update_playback_controls()
            page.update()

            await animate_physical_turn(inv_move)
            update_playback_controls()
            page.update()

    async def autoplay_task():
        is_animating[0] = True
        update_playback_controls()
        page.update()
        while is_animating[0] and is_open[0] and step_index[0] < len(solution_steps):
            await step_forward_task()
            if not is_animating[0] or step_index[0] >= len(solution_steps):
                break
            await asyncio.sleep(SPEED_PRESETS[speed_idx[0]][2])
        is_animating[0] = False
        update_playback_controls()
        page.update()

    def on_next_click(e):
        if not is_animating[0] and not is_turning[0]:
            page.run_task(step_forward_task)

    def on_prev_click(e):
        if not is_animating[0] and not is_turning[0]:
            page.run_task(step_backward_task)

    def on_play_click(e):
        if is_animating[0]:
            is_animating[0] = False
            update_playback_controls()
            page.update()
        elif not is_turning[0]:
            page.run_task(autoplay_task)

    prev_btn.on_click = on_prev_click
    next_btn.on_click = on_next_click
    play_btn.on_click = on_play_click

    def on_solve_click(e):
        if is_turning[0] or cam_state["active"]:
            return
        is_animating[0] = False

        if not cube.is_color_count_valid():
            counts = cube.color_counts()
            invalid = ", ".join(
                f"{FACE_COLOR_NAMES[c]} ({counts[c]}/9)"
                for c in ["U", "R", "F", "D", "L", "B"]
                if counts[c] != 9
            )
            status_banner.value = f"❌ No se puede resolver: cada color debe tener 9/9. Revisa: {invalid}"
            status_banner.color = "#FF5252"
            page.update()
            return

        state_str = cube.to_kociemba_string()
        if state_str == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB":
            status_banner.value = "✅ El cubo ya está resuelto. Usa 'Mezclar' o 'Armar Manualmente'."
            status_banner.color = "#00E676"
            page.update()
            return

        try:
            raw_solution = kociemba.solve(state_str)
            steps = raw_solution.strip().split()
            solution_steps.clear()
            solution_steps.extend(steps)
            step_index[0] = 0
            status_banner.value = f"✅ Solución óptima encontrada en {len(steps)} movimientos."
            status_banner.color = "#00E676"
            step_instruction.value = f"Primer paso: {steps[0]}  →  {MOVE_EXPLANATIONS[steps[0]]}"
            update_playback_controls()
        except Exception:
            status_banner.value = (
                "❌ Combinación físicamente imposible (esquina/arista invertida o permutación inválida). Revisa las pegatinas."
            )
            status_banner.color = "#FF5252"
            solution_steps.clear()
            step_index[0] = 0
            update_playback_controls()
        page.update()

    def on_reset(e):
        if is_turning[0] or cam_state["active"]:
            return
        is_animating[0] = False
        cube.reset()
        solution_steps.clear()
        step_index[0] = 0
        selected_brush[0] = None
        hide_palette_after_scan[0] = False
        cam_rot[0] = _make_cam_mat(-0.62, 0.44)
        brush_section.visible = not manual_solve_mode[0]
        reset_btn.visible = True
        scramble_btn.visible = True
        back_to_main_btn.visible = False
        step_instruction.value = "Estado inicial: Cubo resuelto (9/9 en cada color)"
        status_banner.value = "Cubo reiniciado."
        status_banner.color = "#80DEEA"
        update_playback_controls()
        update_brush_ui()
        render_3d_cube()
        page.update()

    async def scramble_task():
        if is_animating[0] or is_turning[0] or cam_state["active"]:
            return
        solution_steps.clear()
        step_index[0] = 0
        update_playback_controls()
        status_banner.value = "🎲 Mezclando cubo aleatoriamente..."
        status_banner.color = "#FFD54F"
        page.update()

        last_base = ""
        for _ in range(16):
            if not is_open[0] or cam_state["active"]:
                break
            candidates = [m for m in ALL_STANDARD_MOVES if m[0] != last_base]
            mv = random.choice(candidates)
            last_base = mv[0]
            await animate_physical_turn(mv, duration=0.075)

        if manual_solve_mode[0]:
            status_banner.value = "🎮 Cubo mezclado: desliza bordes para filas/columnas o el centro para girar esa cara."
        else:
            step_instruction.value = "Cubo mezclado — Presiona 'Armar Manualmente' o 'Calcular Solución'"
            status_banner.value = "✨ Cubo listo para armar manualmente o calcular solución óptima."
        status_banner.color = "#80DEEA"
        update_brush_ui()
        page.update()

    def on_scramble_click(e):
        if not is_animating[0] and not is_turning[0] and not cam_state["active"]:
            page.run_task(scramble_task)

    async def manual_turn_task(move: str):
        if is_animating[0] or is_turning[0] or cam_state["active"]:
            return
        solution_steps.clear()
        step_index[0] = 0
        update_playback_controls()
        await animate_physical_turn(move)

        if cube.to_kociemba_string() == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB":
            play_victory_sound(sound_enabled[0])
            step_instruction.value = "🎉 ¡Armaste el cubo manualmente!"
            status_banner.value = "🎉 ¡Excelente! Armaste el cubo manualmente. Pulsa 'Mezclar' para jugar otra vez."
            status_banner.color = "#00E676"
        else:
            step_instruction.value = f"Giro manual: {move} — {MOVE_EXPLANATIONS[move]}"
            status_banner.value = f"Giro {move} ({MOVE_EXPLANATIONS[move]})"
            status_banner.color = "#80DEEA"
        page.update()

    def trigger_manual_move(move: str):
        if not is_animating[0] and not is_turning[0] and not cam_state["active"]:
            page.run_task(manual_turn_task, move)

    camera_preview = ft.Image(
        src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
        width=280,
        height=280,
        fit="contain",
        border_radius=12,
        gapless_playback=True,
    )

    cam_capture_btn = ft.FilledButton(
        "Capturar Cara (Espacio)",
        icon=ft.Icons.CAMERA,
        style=ft.ButtonStyle(bgcolor="#00C853", color="#000000"),
    )
    cam_prev_btn = ft.OutlinedButton("Anterior", icon=ft.Icons.SKIP_PREVIOUS)
    cam_cancel_btn = ft.OutlinedButton("Volver", icon=ft.Icons.ARROW_BACK)

    camera_panel = ft.Column(
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
        controls=[
            ft.Container(
                bgcolor="#22222B",
                border_radius=14,
                padding=14,
                border=ft.Border.all(1, "#323242"),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=24,
                    controls=[
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                            controls=[
                                ft.Text("Cámara en vivo", size=12, weight=ft.FontWeight.BOLD, color="#00E5FF"),
                                ft.Container(
                                    content=camera_preview,
                                    border=ft.Border.all(2, "#00E5FF"),
                                    border_radius=14,
                                    padding=4,
                                    bgcolor="#000000",
                                ),
                            ],
                        ),
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                            controls=[
                                ft.Text("Vista previa 3D", size=12, weight=ft.FontWeight.BOLD, color="#80DEEA"),
                                interactive_mini_cube,
                                ft.Text("Arrastra en 360° para girar", size=10, color="#9E9E9E"),
                            ],
                        ),
                    ],
                ),
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[cam_capture_btn, cam_prev_btn, cam_cancel_btn],
            ),
        ],
    )

    manual_play_section = ft.Column(
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=6,
        controls=[
            ft.Text(
                "Desliza bordes para girar filas/columnas, el centro para girar la cara, o usa botones / teclado:",
                size=11,
                color="#80DEEA",
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Container(
                        bgcolor="#2A2A34",
                        border_radius=7,
                        padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                        border=ft.Border.all(1, COLORS[face]),
                        content=ft.Row(
                            tight=True,
                            spacing=4,
                            controls=[
                                ft.Container(
                                    width=8,
                                    height=8,
                                    border_radius=4,
                                    bgcolor=COLORS[face],
                                ),
                                ft.Container(
                                    padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                                    border_radius=4,
                                    bgcolor="#1E1E26",
                                    tooltip=MOVE_EXPLANATIONS[face],
                                    on_click=lambda e, m=face: trigger_manual_move(m),
                                    content=ft.Text(f"{face}↻", size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                ),
                                ft.Container(
                                    padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                                    border_radius=4,
                                    bgcolor="#1E1E26",
                                    tooltip=MOVE_EXPLANATIONS[f"{face}'"],
                                    on_click=lambda e, m=f"{face}'": trigger_manual_move(m),
                                    content=ft.Text(f"{face}↺", size=11, weight=ft.FontWeight.BOLD, color="#B0BEC5"),
                                ),
                            ],
                        ),
                    )
                    for face in ["U", "F", "R", "L", "B", "D"]
                ],
            ),
        ],
    )

    manual_mode_btn = ft.FilledTonalButton(
        "Armar Manualmente",
        icon=ft.Icons.SPORTS_ESPORTS,
    )

    playback_box = ft.Container(
        bgcolor="#25252D",
        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
        border_radius=12,
        width=620,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            controls=[
                step_instruction,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    controls=[prev_btn, play_btn, next_btn, progress_text],
                ),
            ],
        ),
    )

    reset_btn = ft.OutlinedButton("Reiniciar", icon=ft.Icons.REFRESH, on_click=on_reset)
    scramble_btn = ft.OutlinedButton("Mezclar", icon=ft.Icons.SHUFFLE, on_click=on_scramble_click)
    scan_cam_btn = ft.FilledTonalButton("Escanear Cámara", icon=ft.Icons.CAMERA_ALT)

    back_to_main_btn = ft.OutlinedButton(
        "Principal",
        icon=ft.Icons.ARROW_BACK,
        visible=False,
        tooltip="Volver a la pantalla principal",
    )

    def go_to_main_screen(e=None):
        if is_turning[0]:
            return
        is_animating[0] = False
        cam_state["active"] = False
        hide_palette_after_scan[0] = False
        manual_solve_mode[0] = False
        selected_brush[0] = None

        camera_panel.visible = False
        cube_view_panel.visible = True
        brush_section.visible = True
        manual_play_section.visible = False
        playback_box.visible = True
        action_bar.visible = True
        reset_btn.visible = True
        scramble_btn.visible = True
        scan_cam_btn.visible = True
        solve_btn.visible = True
        back_to_main_btn.visible = False
        manual_mode_btn.text = "Armar Manualmente"
        manual_mode_btn.icon = ft.Icons.SPORTS_ESPORTS

        status_banner.value = "Elige un color de la paleta para pintar, o usa 'Armar Manualmente' / 'Escanear Cámara'."
        status_banner.color = "#80DEEA"
        update_playback_controls()
        update_brush_ui()
        render_3d_cube()
        page.update()

    back_to_main_btn.on_click = go_to_main_screen

    def set_manual_solve_mode(enabled: bool):
        manual_solve_mode[0] = enabled
        brush_section.visible = (not enabled) and (not hide_palette_after_scan[0])
        manual_play_section.visible = enabled
        playback_box.visible = not enabled
        scan_cam_btn.visible = not enabled
        solve_btn.visible = not enabled
        reset_btn.visible = not hide_palette_after_scan[0]
        scramble_btn.visible = not hide_palette_after_scan[0]

        if enabled:
            manual_mode_btn.text = "Volver"
            manual_mode_btn.icon = ft.Icons.ARROW_BACK
            status_banner.value = "🎮 Modo Armado Manual: desliza bordes para filas/columnas o el centro para girar la cara."
            status_banner.color = "#00E676"
        else:
            manual_mode_btn.text = "Armar Manualmente"
            manual_mode_btn.icon = ft.Icons.SPORTS_ESPORTS
            if hide_palette_after_scan[0]:
                status_banner.value = "Cubo escaneado listo — Presiona 'Calcular Solución' o 'Armar Manualmente'."
            else:
                status_banner.value = "Elige un color de la paleta para pintar, o usa 'Armar Manualmente'."
            status_banner.color = "#80DEEA"
            update_brush_ui()
        page.update()

    manual_mode_btn.on_click = lambda e: set_manual_solve_mode(not manual_solve_mode[0])

    cube_view_panel = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=6,
        controls=[
            interactive_cube,
            brush_section,
            manual_play_section,
            playback_box,
        ],
    )

    solve_btn.on_click = on_solve_click

    def exit_camera_mode(completed: bool = False):
        cam_state["active"] = False
        camera_panel.visible = False
        cube_view_panel.visible = True
        action_bar.visible = True

        if completed and len(cam_state["scanned_faces"]) == 6:
            reclassified = reclassify_all_faces(cam_state["raw_labs"], cam_state["calibrated_labs"])
            for f_code, stickers in reclassified.items():
                cube.faces[f_code] = list(stickers)
            solution_steps.clear()
            step_index[0] = 0
            manual_solve_mode[0] = False

            hide_palette_after_scan[0] = True
            brush_section.visible = False
            manual_play_section.visible = False
            playback_box.visible = True
            reset_btn.visible = False
            scramble_btn.visible = False
            scan_cam_btn.visible = True
            solve_btn.visible = True
            back_to_main_btn.visible = True
            manual_mode_btn.text = "Armar Manualmente"
            manual_mode_btn.icon = ft.Icons.SPORTS_ESPORTS
            update_playback_controls()
            update_brush_ui()
            render_3d_cube()

            if cube.is_color_count_valid():
                status_banner.value = "✅ ¡6 caras escaneadas! Presiona 'Calcular Solución' o 'Armar Manualmente'."
                status_banner.color = "#00E676"
            else:
                counts = cube.color_counts()
                invalid = ", ".join(
                    f"{FACE_COLOR_NAMES[c]} ({counts[c]}/9)"
                    for c in ["U", "R", "F", "D", "L", "B"]
                    if counts[c] != 9
                )
                status_banner.value = f"⚠️ Escaneo completado con diferencia de conteo: {invalid}"
                status_banner.color = "#FFD54F"
        else:
            brush_section.visible = (not manual_solve_mode[0]) and (not hide_palette_after_scan[0])
            manual_play_section.visible = manual_solve_mode[0]
            playback_box.visible = not manual_solve_mode[0]
            reset_btn.visible = not hide_palette_after_scan[0]
            scramble_btn.visible = not hide_palette_after_scan[0]
            scan_cam_btn.visible = not manual_solve_mode[0]
            solve_btn.visible = not manual_solve_mode[0]
            back_to_main_btn.visible = hide_palette_after_scan[0]
            status_banner.value = "Escaneo cancelado."
            status_banner.color = "#80DEEA"
            update_playback_controls()
            update_brush_ui()

        page.update()

    def capture_current_face(e=None):
        if not cam_state["active"]:
            return
        face_code = cam_state.get("detected_center", "F")
        if face_code in cam_state["scanned_faces"]:
            faltan = ", ".join(
                FACE_COLOR_NAMES[c]
                for c in ["F", "R", "B", "L", "U", "D"]
                if c not in cam_state["scanned_faces"]
            )
            status_banner.value = f"✓ {FACE_COLOR_NAMES[face_code]} ya capturada • Pendientes: {faltan}"
            status_banner.color = "#80DEEA"
            page.update()
            return

        cam_state["scanned_faces"][face_code] = list(cam_state["latest_9"])
        cam_state.setdefault("capture_history", []).append(face_code)
        if cam_state["latest_labs"]:
            cam_state["raw_labs"][face_code] = list(cam_state["latest_labs"])
            cam_state["calibrated_labs"][face_code] = cam_state["latest_labs"][4]
        play_turn_click(sound_enabled[0])
        mini_manual_orbit[0] = False

        total_done = len(cam_state["scanned_faces"])
        if total_done >= 6:
            exit_camera_mode(completed=True)
        else:
            faltan = ", ".join(
                FACE_COLOR_NAMES[c]
                for c in ["F", "R", "B", "L", "U", "D"]
                if c not in cam_state["scanned_faces"]
            )
            status_banner.value = f"✓ {FACE_COLOR_NAMES[face_code]} guardada ({total_done}/6) • Pendientes: {faltan}"
            status_banner.color = "#80DEEA"
            page.update()

    def prev_camera_face(e=None):
        history = cam_state.get("capture_history", [])
        if cam_state["active"] and history:
            last_face = history.pop()
            cam_state["scanned_faces"].pop(last_face, None)
            cam_state["raw_labs"].pop(last_face, None)
            mini_manual_orbit[0] = False
            total_done = len(cam_state["scanned_faces"])
            status_banner.value = f"↩️ Cara {FACE_COLOR_NAMES[last_face]} deshecha ({total_done}/6)."
            status_banner.color = "#80DEEA"
            page.update()

    cam_capture_btn.on_click = capture_current_face
    cam_prev_btn.on_click = prev_camera_face
    cam_cancel_btn.on_click = lambda e: exit_camera_mode(completed=False)

    def on_key_event(e: ft.KeyboardEvent):
        if not is_open[0]:
            return
        if cam_state["active"]:
            if e.key == " ":
                capture_current_face()
            elif e.key == "Escape":
                exit_camera_mode(completed=False)
            return

        key_upper = (e.key or "").upper()
        if key_upper in ("U", "D", "F", "B", "L", "R"):
            if not manual_solve_mode[0]:
                set_manual_solve_mode(True)
            move = key_upper + ("'" if e.shift else "")
            trigger_manual_move(move)

    page.on_keyboard_event = on_key_event

    async def camera_stream_loop():
        active_idx = cam_state["cam_idx"]
        cap = await asyncio.to_thread(open_camera_capture, active_idx)
        last_banner_text = ""

        while cam_state["active"] and is_open[0]:
            if cam_state["cam_idx"] != active_idx:
                await asyncio.to_thread(cap.release)
                active_idx = cam_state["cam_idx"]
                cap = await asyncio.to_thread(open_camera_capture, active_idx)

            ret, frame = await asyncio.to_thread(cap.read)
            if ret and frame is not None and len(cam_state["scanned_faces"]) < 6:
                b64_img, detected_9, patches_lab, detected_center, is_new_face = await asyncio.to_thread(
                    process_camera_frame,
                    frame,
                    cam_state["calibrated_labs"],
                    set(cam_state["scanned_faces"].keys()),
                )
                cam_state["latest_9"] = detected_9
                cam_state["latest_labs"] = patches_lab
                cam_state["detected_center"] = detected_center
                cam_state["center_valid"] = is_new_face

                if cam_capture_btn.disabled != (not is_new_face):
                    cam_capture_btn.disabled = not is_new_face
                    if cam_capture_btn.page:
                        cam_capture_btn.update()

                if not mini_manual_orbit[0]:
                    target_yaw, target_pitch = FACE_3D_ANGLES[detected_center]
                    target_mat = _make_cam_mat(target_yaw, target_pitch)
                    for r_i in range(3):
                        for c_i in range(3):
                            mini_rot[0][r_i][c_i] += (target_mat[r_i][c_i] - mini_rot[0][r_i][c_i]) * 0.35

                total_done = len(cam_state["scanned_faces"])
                if is_new_face:
                    new_text = (
                        f"📷 ({total_done}/6) Cara {FACE_COLOR_NAMES[detected_center]} lista — "
                        f"Presiona Capturar Cara o Espacio"
                    )
                    new_color = "#00E676"
                else:
                    faltan = ", ".join(
                        FACE_COLOR_NAMES[c]
                        for c in ["F", "R", "B", "L", "U", "D"]
                        if c not in cam_state["scanned_faces"]
                    )
                    new_text = (
                        f"✓ {FACE_COLOR_NAMES[detected_center]} guardada ({total_done}/6) • "
                        f"Gira a una cara pendiente: {faltan}"
                    )
                    new_color = "#80DEEA"

                if new_text != last_banner_text:
                    last_banner_text = new_text
                    status_banner.value = new_text
                    status_banner.color = new_color
                    if status_banner.page:
                        status_banner.update()

                camera_preview.src = f"data:image/jpeg;base64,{b64_img}"
                if camera_preview.page:
                    camera_preview.update()

                render_mini_3d_guide(detected_center, detected_9, cam_state["scanned_faces"])
                if mini_cube_canvas.page:
                    mini_cube_canvas.update()

            await asyncio.sleep(0.05)

        await asyncio.to_thread(cap.release)

    async def start_camera_mode():
        is_animating[0] = False
        status_banner.value = "📷 Detectando cámaras disponibles..."
        status_banner.color = "#80DEEA"
        page.update()

        available_cams = await asyncio.to_thread(detect_available_cameras)
        cam_state["available_cams"] = available_cams
        cam_state["cam_pos"] = 0
        cam_state["cam_idx"] = available_cams[0]
        cam_state["scanned_faces"] = {}
        cam_state["capture_history"] = []
        cam_state["raw_labs"] = {}
        cam_state["calibrated_labs"] = dict(DEFAULT_LAB_REFS)
        cam_state["detected_center"] = "F"
        cam_state["center_valid"] = True
        cam_state["active"] = True
        cam_capture_btn.disabled = False

        mini_rot[0] = _make_cam_mat(*FACE_3D_ANGLES["F"])
        mini_manual_orbit[0] = False

        cube_view_panel.visible = False
        brush_section.visible = False
        manual_play_section.visible = False
        playback_box.visible = False
        action_bar.visible = False
        camera_panel.visible = True
        back_to_main_btn.visible = True
        update_playback_controls()

        status_banner.value = "📷 (0/6) Muestra cualquier cara del cubo frente a la cámara (Blanco arriba)"
        page.update()

        page.run_task(camera_stream_loop)

    def on_camera_scan_click(e):
        if not is_turning[0] and not cam_state["active"]:
            page.run_task(start_camera_mode)

    scan_cam_btn.on_click = on_camera_scan_click

    action_bar = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=8,
        wrap=True,
        controls=[
            reset_btn,
            scramble_btn,
            manual_mode_btn,
            scan_cam_btn,
            solve_btn,
        ],
    )

    def close_modal(e=None):
        is_open[0] = False
        is_animating[0] = False
        cam_state["active"] = False
        page.on_keyboard_event = None
        if modal_overlay in page.overlay:
            page.overlay.remove(modal_overlay)
            page.update()

    sound_btn = ft.IconButton(
        icon=ft.Icons.VOLUME_UP,
        icon_color="#80DEEA",
        tooltip="Silenciar / Activar sonidos",
    )

    def toggle_sound(e):
        sound_enabled[0] = not sound_enabled[0]
        sound_btn.icon = ft.Icons.VOLUME_UP if sound_enabled[0] else ft.Icons.VOLUME_OFF
        sound_btn.icon_color = "#80DEEA" if sound_enabled[0] else "#9E9E9E"
        page.update()

    sound_btn.on_click = toggle_sound

    render_3d_cube()
    update_brush_ui()

    dialog_card = ft.Container(
        width=680,
        height=725,
        bgcolor="#1A1A22",
        border_radius=18,
        padding=18,
        border=ft.Border.all(1, "#3A3A4A"),
        shadow=ft.BoxShadow(blur_radius=30, color="#000000"),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.VIEW_IN_AR, color="#00E5FF"),
                                ft.Text("Solucionador Cubo de Rubik 3D", size=18, weight=ft.FontWeight.BOLD),
                            ],
                        ),
                        ft.Row(
                            spacing=8,
                            controls=[
                                back_to_main_btn,
                                speed_btn,
                                sound_btn,
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    bgcolor="#D50000",
                                    icon_color="#FFFFFF",
                                    tooltip="Cerrar",
                                    on_click=close_modal,
                                ),
                            ],
                        ),
                    ],
                ),
                status_banner,
                cube_view_panel,
                camera_panel,
                action_bar,
            ],
        ),
    )

    modal_overlay = ft.Container(
        bgcolor="#B3000000",
        expand=True,
        alignment=ft.Alignment(0, 0),
        content=dialog_card,
    )

    page.overlay.append(modal_overlay)
    page.update()