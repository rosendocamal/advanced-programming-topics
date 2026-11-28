import base64, sys, cv2
import numpy as np


def open_camera_capture(idx: int):
    """Usa AVFoundation en macOS y el backend nativo por defecto en Windows/Linux."""
    if sys.platform == "darwin":
        return cv2.VideoCapture(idx, cv2.CAP_AVFOUNDATION)
    return cv2.VideoCapture(idx)


SCAN_ORDER = [
    ("F", "1/6: Cara VERDE al frente (Blanco arriba)"),
    ("R", "2/6: Cara ROJA al frente (Blanco arriba)"),
    ("B", "3/6: Cara AZUL al frente (Blanco arriba)"),
    ("L", "4/6: Cara NARANJA al frente (Blanco arriba)"),
    ("U", "5/6: Cara BLANCA al frente"),
    ("D", "6/6: Cara AMARILLA al frente"),
]

FACE_COLOR_NAMES = {
    "U": "BLANCO",
    "R": "ROJO",
    "F": "VERDE",
    "D": "AMARILLO",
    "L": "NARANJA",
    "B": "AZUL",
}

BGR_PREVIEW = {
    "U": (255, 255, 255),
    "R": (35, 35, 235),
    "F": (45, 200, 55),
    "D": (0, 235, 255),
    "L": (0, 125, 255),
    "B": (235, 110, 25),
}

DEFAULT_LAB_REFS = {
    "U": np.array([225.0, 128.0, 128.0], dtype=np.float32),
    "R": np.array([115.0, 185.0, 165.0], dtype=np.float32),
    "F": np.array([145.0, 82.0, 162.0], dtype=np.float32),
    "D": np.array([210.0, 118.0, 195.0], dtype=np.float32),
    "L": np.array([155.0, 162.0, 182.0], dtype=np.float32),
    "B": np.array([105.0, 145.0, 75.0], dtype=np.float32),
}


def extract_patch_lab(roi_bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV).reshape(-1, 3)
    bgr_flat = roi_bgr.reshape(-1, 3)

    v_vals = hsv[:, 2]
    low_v = np.percentile(v_vals, 10)
    high_v = np.percentile(v_vals, 70)
    mask = (v_vals >= low_v) & (v_vals <= max(high_v, low_v + 10))
    clean_bgr = bgr_flat[mask] if np.any(mask) else bgr_flat

    med_bgr = np.median(clean_bgr, axis=0).astype(np.uint8)
    return cv2.cvtColor(med_bgr.reshape(1, 1, 3), cv2.COLOR_BGR2LAB)[0][0].astype(np.float32)


def classify_lab_sample(sample_lab: np.ndarray, calibrated_labs: dict[str, np.ndarray]) -> str:
    best_code = "U"
    best_dist = float("inf")

    for code, ref_lab in calibrated_labs.items():
        diff = sample_lab - ref_lab
        dist = (0.45 * diff[0] ** 2) + (1.35 * diff[1] ** 2) + (1.35 * diff[2] ** 2)
        if dist < best_dist:
            best_dist = dist
            best_code = code
    return best_code


def reclassify_all_faces(
    raw_labs_by_face: dict[str, list[np.ndarray]],
    calibrated_labs: dict[str, np.ndarray],
) -> dict[str, list[str]]:
    final_faces: dict[str, list[str]] = {}
    for face_code, patches_lab in raw_labs_by_face.items():
        codes = [classify_lab_sample(p_lab, calibrated_labs) for p_lab in patches_lab]
        codes[4] = face_code
        final_faces[face_code] = codes
    return final_faces


def detect_available_cameras() -> list[int]:
    """Devuelve la lista ordenada de índices de cámara funcionales en el sistema."""
    available: list[tuple[int, int, int]] = []
    for idx in (0, 1, 2):
        cap = open_camera_capture(idx)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w = frame.shape[:2]
                available.append((idx, w, h))
            cap.release()

    if not available:
        return [0]

    if sys.platform == "darwin" and len(available) > 1:
        available.sort(key=lambda item: 0 if abs((item[1] / float(item[2])) - (16.0 / 9.0)) < 0.08 else 1)

    return [item[0] for item in available]


def find_mac_camera_index() -> int:
    return detect_available_cameras()[0]


def process_camera_frame(
    frame,
    calibrated_labs: dict[str, np.ndarray],
    scanned_faces: set[str] | None = None,
) -> tuple[str, list[str], list[np.ndarray], str, bool]:
    # Efecto espejo para que mover la mano a la derecha se vea a la derecha en pantalla
    frame = cv2.flip(frame, 1)
    h_raw, w_raw, _ = frame.shape

    crop_size = int(min(h_raw, w_raw) * 0.54)
    cx_raw, cy_raw = w_raw // 2, h_raw // 2
    half = crop_size // 2
    square = frame[cy_raw - half : cy_raw + half, cx_raw - half : cx_raw + half]

    square = cv2.resize(square, (300, 300))
    blurred = cv2.GaussianBlur(square, (5, 5), 0)

    # Identifica qué cara estás mostrando por su centro real (permite empezar con cualquier cara)
    center_roi = blurred[125:175, 125:175]
    center_lab = extract_patch_lab(center_roi)
    detected_center_code = classify_lab_sample(center_lab, calibrated_labs)
    is_new_face = scanned_faces is None or (detected_center_code not in scanned_faces)

    live_refs = dict(calibrated_labs)
    if is_new_face:
        live_refs[detected_center_code] = center_lab

    cell = 100
    detected_9: list[str] = []
    patches_lab_9: list[np.ndarray] = []

    for row in range(3):
        row_items = []
        for col in range(3):
            x0 = col * cell
            y0 = row * cell
            cx = x0 + cell // 2
            cy = y0 + cell // 2
            r = 22

            roi = blurred[cy - r : cy + r, cx - r : cx + r]
            p_lab = extract_patch_lab(roi)
            code = detected_center_code if (row == 1 and col == 1) else classify_lab_sample(p_lab, live_refs)
            row_items.append((code, p_lab))

            cv2.rectangle(square, (x0 + 2, y0 + 2), (x0 + cell - 2, y0 + cell - 2), (20, 20, 20), 4)
            cv2.rectangle(square, (x0 + 3, y0 + 3), (x0 + cell - 3, y0 + cell - 3), BGR_PREVIEW[code], 2)
            cv2.circle(square, (cx, cy), 6, BGR_PREVIEW[code], -1)

        # Invertir horizontalmente al guardar para compensar el espejo visual
        for c_code, c_lab in reversed(row_items):
            detected_9.append(c_code)
            patches_lab_9.append(c_lab)

    _, buffer = cv2.imencode(".jpg", square, [cv2.IMWRITE_JPEG_QUALITY, 80])
    b64_str = base64.b64encode(buffer).decode("utf-8")
    return b64_str, detected_9, patches_lab_9, detected_center_code, is_new_face