import io
import math
import os
import platform
import struct
import subprocess
import tempfile
import threading
import wave


def _generate_wav_bytes(samples: list[float], sample_rate: int = 22050) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        raw = b"".join(
            struct.pack("<h", max(-32767, min(32767, int(s * 32767))))
            for s in samples
        )
        wf.writeframes(raw)
    return buf.getvalue()


def _build_click_wav() -> str:
    sr = 22050
    duration = 0.045
    total = int(sr * duration)
    samples = []
    for i in range(total):
        t = i / sr
        env = math.exp(-t * 95.0)
        # Mezcla de frecuencia grave (plástico) + aguda (encaje)
        val = (
            0.55 * math.sin(2.0 * math.pi * 420.0 * t)
            + 0.45 * math.sin(2.0 * math.pi * 1350.0 * t)
        ) * env * 0.45
        samples.append(val)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(_generate_wav_bytes(samples, sr))
    tmp.close()
    return tmp.name


def _build_victory_wav() -> str:
    sr = 22050
    notes = [523.25, 659.25, 783.99, 1046.50]  # Do5 - Mi5 - Sol5 - Do6
    note_dur = 0.11
    samples = []
    for idx, freq in enumerate(notes):
        dur = note_dur if idx < 3 else 0.32
        count = int(sr * dur)
        for i in range(count):
            t = i / sr
            env = math.exp(-t * (8.0 if idx < 3 else 4.5))
            val = math.sin(2.0 * math.pi * freq * t) * env * 0.40
            samples.append(val)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(_generate_wav_bytes(samples, sr))
    tmp.close()
    return tmp.name


_CLICK_PATH = _build_click_wav()
_VICTORY_PATH = _build_victory_wav()


def _play_file_async(filepath: str):
    def worker():
        sys_name = platform.system()
        try:
            if sys_name == "Darwin":
                subprocess.run(
                    ["afplay", filepath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            elif sys_name == "Windows":
                import winsound
                winsound.PlaySound(filepath, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                subprocess.run(
                    ["aplay", "-q", filepath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception:
            pass

    threading.Thread(target=worker, daemon=True).start()


def play_turn_click(enabled: bool = True):
    if enabled and os.path.exists(_CLICK_PATH):
        _play_file_async(_CLICK_PATH)


def play_victory_sound(enabled: bool = True):
    if enabled and os.path.exists(_VICTORY_PATH):
        _play_file_async(_VICTORY_PATH)