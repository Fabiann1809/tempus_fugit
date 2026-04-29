import tkinter as tk
import datetime

from features.analog_clock import AnalogClock
from features.stopwatch import Stopwatch
from features.alarm import Alarm
from features.countdown import Countdown
from utils.time_helpers import format_hms, format_date_es, format_year


class AppWindow:

    APP_BG       = "#2C1810"
    WOOD_BG      = "#6B3410"
    WOOD_BORDER  = "#A0522D"
    GOLD         = "#D4AF37"
    MUTED_GOLD   = "#8B6914"
    DARK_GOLD    = "#B8860B"
    PANEL_BG     = "#1a0e06"
    PANEL_BORDER = "#5C3A1E"
    DEEP_WOOD    = "#3D1F0A"
    BTN_BG       = "#3D1F0A"
    BTN_ACTIVE   = "#5C2E0E"

    TAB_NAMES = ("RELOJ", "CRONO", "ALARMA", "CUENTA")

    def __init__(self, root: tk.Tk):
        self._root = root
        self._clock_after_id: str | None = None
        self._active_tab = 0
        self._manual_time: datetime.datetime | None = None

        self._setup_root()
        self._build_layout()
        self._start_clock_loop()

    def _setup_root(self):
        self._root.title("Tempus Fugit")
        self._root.configure(bg=self.APP_BG)
        self._root.resizable(False, False)
        self._root.update_idletasks()
        w, h = 360, 640
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        self._root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build_layout(self):
        root = self._root

        outer = tk.Frame(root, bg=self.WOOD_BG, bd=3, relief="ridge",
                         highlightbackground=self.WOOD_BORDER,
                         highlightthickness=2)
        outer.pack(fill="both", expand=True, padx=8, pady=8)

        tk.Label(
            outer,
            text=" T E M P U S   F U G I T ",
            bg=self.WOOD_BG, fg=self.GOLD,
            font=("Georgia", 13, "bold"),
        ).pack(pady=(10, 2))

        tk.Label(
            outer,
            text="✦ · · ✦ · · ✦",
            bg=self.WOOD_BG, fg=self.MUTED_GOLD,
            font=("Georgia", 9),
        ).pack(pady=(0, 8))

        clock_container = tk.Frame(outer, bg=self.WOOD_BG)
        clock_container.pack()
        self._analog = AnalogClock(clock_container)
        self._analog.pack()

        strip_outer = tk.Frame(outer, bg=self.PANEL_BORDER, bd=1)
        strip_outer.pack(fill="x", padx=16, pady=(8, 4))

        strip = tk.Frame(strip_outer, bg=self.PANEL_BG)
        strip.pack(fill="x", padx=1, pady=1)

        self._time_var = tk.StringVar(value="00:00:00")
        tk.Label(
            strip,
            textvariable=self._time_var,
            bg=self.PANEL_BG, fg=self.GOLD,
            font=("Courier New", 22),
            padx=10, pady=4,
        ).pack(side="left")

        date_frame = tk.Frame(strip, bg=self.PANEL_BG)
        date_frame.pack(side="right", padx=10)

        self._date_var = tk.StringVar(value="LUN 01 ENE")
        tk.Label(
            date_frame,
            textvariable=self._date_var,
            bg=self.PANEL_BG, fg=self.MUTED_GOLD,
            font=("Courier New", 11),
        ).pack(anchor="e")

        self._year_var = tk.StringVar(value="2024")
        tk.Label(
            date_frame,
            textvariable=self._year_var,
            bg=self.PANEL_BG, fg=self.PANEL_BORDER,
            font=("Courier New", 11),
        ).pack(anchor="e")

        tab_bar = tk.Frame(outer, bg=self.PANEL_BG)
        tab_bar.pack(fill="x", pady=(8, 0))

        self._tab_btns: list[tk.Button] = []
        for i, name in enumerate(self.TAB_NAMES):
            btn = tk.Button(
                tab_bar,
                text=name,
                font=("Georgia", 9, "bold"),
                bg=self.PANEL_BG, fg=self.MUTED_GOLD,
                activebackground=self.DEEP_WOOD,
                activeforeground=self.GOLD,
                relief="flat", bd=0,
                padx=0, pady=6,
                cursor="hand2",
                command=lambda idx=i: self._switch_tab(idx),
            )
            btn.pack(side="left", fill="x", expand=True)
            self._tab_btns.append(btn)

        tk.Frame(outer, bg=self.PANEL_BORDER, height=1).pack(fill="x")

        content_area = tk.Frame(outer, bg=self.APP_BG)
        content_area.pack(fill="both", expand=True)

        self._reloj_frame = self._build_reloj_panel(content_area)

        self._stopwatch = Stopwatch(content_area)
        self._alarm = Alarm(content_area, on_trigger=self._analog.flash_border)
        self._countdown = Countdown(content_area, on_trigger=self._analog.flash_border)

        self._analog.on_drag = self._on_clock_drag

        self._panels = [
            self._reloj_frame,
            self._stopwatch.frame,
            self._alarm.frame,
            self._countdown.frame,
        ]

        self._switch_tab(0)

    def _build_reloj_panel(self, parent: tk.Widget) -> tk.Frame:
        frame = tk.Frame(parent, bg=self.APP_BG)

        tk.Label(
            frame, text="— ajuste de hora —",
            bg=self.APP_BG, fg=self.PANEL_BORDER,
            font=("Georgia", 9),
        ).pack(pady=(14, 8))

        # Spinbox row: HH : MM : SS
        spin_row = tk.Frame(frame, bg=self.APP_BG)
        spin_row.pack()

        spin_cfg = dict(
            width=3,
            font=("Courier New", 18),
            bg=self.PANEL_BG, fg=self.GOLD,
            insertbackground=self.GOLD,
            buttonbackground=self.BTN_BG,
            relief="flat",
            justify="center",
        )
        sep_cfg = dict(bg=self.APP_BG, fg=self.MUTED_GOLD, font=("Courier New", 18, "bold"))

        now = datetime.datetime.now()

        self._set_h = tk.StringVar(value=f"{now.hour:02d}")
        self._set_m = tk.StringVar(value=f"{now.minute:02d}")
        self._set_s = tk.StringVar(value=f"{now.second:02d}")

        self._spin_h = tk.Spinbox(
            spin_row, from_=0, to=23, wrap=True,
            textvariable=self._set_h, format="%02.0f",
            **spin_cfg,
        )
        self._spin_h.pack(side="left")

        tk.Label(spin_row, text=":", **sep_cfg).pack(side="left", padx=2)

        self._spin_m = tk.Spinbox(
            spin_row, from_=0, to=59, wrap=True,
            textvariable=self._set_m, format="%02.0f",
            **spin_cfg,
        )
        self._spin_m.pack(side="left")

        tk.Label(spin_row, text=":", **sep_cfg).pack(side="left", padx=2)

        self._spin_s = tk.Spinbox(
            spin_row, from_=0, to=59, wrap=True,
            textvariable=self._set_s, format="%02.0f",
            **spin_cfg,
        )
        self._spin_s.pack(side="left")

        # Buttons
        btn_row = tk.Frame(frame, bg=self.APP_BG)
        btn_row.pack(pady=(14, 0))

        btn_cfg = dict(
            font=("Georgia", 9, "bold"),
            bg=self.BTN_BG, fg=self.GOLD,
            activebackground=self.BTN_ACTIVE,
            activeforeground=self.GOLD,
            relief="flat", bd=0,
            padx=12, pady=5,
            cursor="hand2",
        )

        tk.Button(
            btn_row, text="Establecer hora",
            command=self._apply_manual_time, **btn_cfg,
        ).pack(side="left", padx=6)

        tk.Button(
            btn_row, text="Hora local",
            command=self._restore_local_time, **btn_cfg,
        ).pack(side="left", padx=6)

        # Status label: shows whether clock is on manual or local time
        self._reloj_status = tk.StringVar(value="")
        tk.Label(
            frame, textvariable=self._reloj_status,
            bg=self.APP_BG, fg=self.MUTED_GOLD,
            font=("Georgia", 8),
        ).pack(pady=(8, 0))

        return frame

    def _apply_manual_time(self):
        try:
            h = int(self._set_h.get())
            m = int(self._set_m.get())
            s = int(self._set_s.get())
            if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59):
                raise ValueError
        except ValueError:
            self._reloj_status.set("⚠  Hora inválida")
            return

        self._manual_time = datetime.datetime.now().replace(
            hour=h, minute=m, second=s, microsecond=0
        )
        self._reloj_status.set(f"✦  Hora fijada: {h:02d}:{m:02d}:{s:02d}")

    def _restore_local_time(self):
        self._manual_time = None
        now = datetime.datetime.now()
        self._set_h.set(f"{now.hour:02d}")
        self._set_m.set(f"{now.minute:02d}")
        self._set_s.set(f"{now.second:02d}")
        self._reloj_status.set("✦  Hora local activa")

    def _on_clock_drag(self, dt: datetime.datetime):
        self._manual_time = dt
        self._set_h.set(f"{dt.hour:02d}")
        self._set_m.set(f"{dt.minute:02d}")
        self._set_s.set(f"{dt.second:02d}")
        self._time_var.set(format_hms(dt))
        self._reloj_status.set(f"✦  Hora fijada: {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}")

    def _switch_tab(self, index: int):
        if self._active_tab == 1:
            self._stopwatch.stop()
        elif self._active_tab == 3:
            self._countdown.stop()

        for panel in self._panels:
            panel.pack_forget()

        self._panels[index].pack(fill="both", expand=True)
        self._active_tab = index

        for i, btn in enumerate(self._tab_btns):
            btn.config(
                bg=self.DEEP_WOOD if i == index else self.PANEL_BG,
                fg=self.GOLD if i == index else self.MUTED_GOLD,
            )

        if index == 1:
            self._stopwatch.resume()
        elif index == 3:
            self._countdown.resume()

    def _start_clock_loop(self):
        self._tick_clock()

    def _tick_clock(self):
        if self._manual_time is not None:
            # Advance the frozen time by 1 second each tick so hands keep moving
            self._manual_time += datetime.timedelta(seconds=1)
            now = self._manual_time
        else:
            now = datetime.datetime.now()

        self._analog.update_hands(now)
        self._time_var.set(format_hms(now))
        self._date_var.set(format_date_es(now))
        self._year_var.set(format_year(now))
        self._clock_after_id = self._root.after(1000, self._tick_clock)

    def destroy(self):
        if self._clock_after_id:
            self._root.after_cancel(self._clock_after_id)
        self._stopwatch.stop()
        self._alarm.stop()
        self._countdown.stop()
