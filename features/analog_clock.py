import math
import tkinter as tk
import datetime


class AnalogClock:

    DIAMETER = 260
    RADIUS = DIAMETER // 2
    CX = RADIUS
    CY = RADIUS

    FACE_BG       = "#F5E6C8"
    FACE_BORDER   = "#B8860B"
    DECO_RING     = "#C4A882"
    TICK_MAJOR    = "#8B4513"
    TICK_MINOR    = "#C4A882"
    HAND_DARK     = "#3D1F0A"
    SECOND_COLOR  = "#8B0000"
    JEWEL_OUTER   = "#B8860B"
    JEWEL_INNER   = "#3D1F0A"
    NUMERAL_MAJOR = "#5C2E0E"
    NUMERAL_MINOR = "#8B5E3C"

    ROMAN = ["XII", "I", "II", "III", "IV", "V",
             "VI", "VII", "VIII", "IX", "X", "XI"]
    MAJOR_POSITIONS = {0, 3, 6, 9}  # XII, III, VI, IX

    def __init__(self, parent: tk.Widget):
        self._flash_id: str | None = None
        self._flash_state = False

        self.canvas = tk.Canvas(
            parent,
            width=self.DIAMETER,
            height=self.DIAMETER,
            bg="#2C1810",
            highlightthickness=0,
        )
        self._draw_static_face()

    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)

    def update_hands(self, dt: datetime.datetime | None = None):
        if dt is None:
            dt = datetime.datetime.now()
        self._draw_hands(dt)

    def flash_border(self, times: int = 5):
        """Alternate border color gold/red for `times` cycles."""
        if self._flash_id is not None:
            self.canvas.after_cancel(self._flash_id)
        self._flash_count = times * 2
        self._run_flash()

    def _draw_static_face(self):
        cx, cy, r = self.CX, self.CY, self.RADIUS

        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=self.FACE_BG, outline=self.FACE_BORDER, width=4,
            tags="face",
        )

        dr = 108
        self.canvas.create_oval(
            cx - dr, cy - dr, cx + dr, cy + dr,
            fill="", outline=self.DECO_RING, width=1,
            dash=(2, 4), tags="face",
        )

        for i in range(60):
            angle = math.radians(i * 6 - 90)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            if i % 5 == 0:
                r_outer, r_inner = r - 5, r - 18
                color, width = self.TICK_MAJOR, 2
            else:
                r_outer, r_inner = r - 5, r - 11
                color, width = self.TICK_MINOR, 1
            self.canvas.create_line(
                cx + cos_a * r_inner, cy + sin_a * r_inner,
                cx + cos_a * r_outer, cy + sin_a * r_outer,
                fill=color, width=width, tags="face",
            )

        num_r = r - 28
        for idx, numeral in enumerate(self.ROMAN):
            angle = math.radians(idx * 30 - 90)
            nx = cx + math.cos(angle) * num_r
            ny = cy + math.sin(angle) * num_r
            if idx in self.MAJOR_POSITIONS:
                self.canvas.create_text(
                    nx, ny, text=numeral,
                    fill=self.NUMERAL_MAJOR,
                    font=("Georgia", 13, "bold"),
                    tags="face",
                )
            else:
                self.canvas.create_text(
                    nx, ny, text=numeral,
                    fill=self.NUMERAL_MINOR,
                    font=("Georgia", 10),
                    tags="face",
                )

        # Separate oval so flash can recolor just the border without redrawing the face
        self._border_id = self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill="", outline=self.FACE_BORDER, width=4,
            tags="border_ring",
        )

    def _draw_hands(self, dt: datetime.datetime):
        self.canvas.delete("hands")
        cx, cy = self.CX, self.CY

        h = dt.hour % 12
        m = dt.minute
        s = dt.second

        # Fractional angles give smooth continuous movement
        h_angle = math.radians((h * 30) + (m * 0.5) - 90)
        self._draw_hand(cx, cy, h_angle, length=60, width=5,
                        color=self.HAND_DARK, tag="hands")

        m_angle = math.radians((m * 6) + (s * 0.1) - 90)
        self._draw_hand(cx, cy, m_angle, length=88, width=3,
                        color=self.HAND_DARK, tag="hands")

        s_angle = math.radians(s * 6 - 90)
        self._draw_hand(cx, cy, s_angle, length=95, width=1,
                        color=self.SECOND_COLOR, tag="hands", tail=15)

        # Jewel drawn last so it sits on top of all hands
        self.canvas.create_oval(
            cx - 5, cy - 5, cx + 5, cy + 5,
            fill=self.JEWEL_OUTER, outline="", tags="hands",
        )
        self.canvas.create_oval(
            cx - 2, cy - 2, cx + 2, cy + 2,
            fill=self.JEWEL_INNER, outline="", tags="hands",
        )

    def _draw_hand(self, cx, cy, angle, length, width, color, tag, tail=0):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        self.canvas.create_line(
            cx - cos_a * tail, cy - sin_a * tail,
            cx + cos_a * length, cy + sin_a * length,
            fill=color, width=width,
            capstyle=tk.ROUND, tags=tag,
        )

    def _run_flash(self):
        if self._flash_count <= 0:
            self.canvas.itemconfig(self._border_id, outline=self.FACE_BORDER)
            self._flash_id = None
            return
        color = "#D4AF37" if self._flash_count % 2 == 0 else "#8B0000"
        self.canvas.itemconfig(self._border_id, outline=color)
        self._flash_count -= 1
        self._flash_id = self.canvas.after(300, self._run_flash)
