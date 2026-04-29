"""app_window.py — Main Tkinter window, layout, and tab management."""

import tkinter as tk
import datetime

from features.analog_clock import AnalogClock
from features.stopwatch import Stopwatch
from features.alarm import Alarm
from features.countdown import Countdown
from utils.time_helpers import format_hms, format_date_es, format_year


class AppWindow:
    """
    Root application window for Tempus Fugit.

    Builds the full layout:
      1. Wood-frame header with title and decorative separator
      2. Analog clock canvas
      3. Digital time / date strip
      4. Four-tab navigation bar
      5. Tab content panels (RELOJ, CRONO, ALARMA, CUENTA)

    The RELOJ tab is always active regardless of which content tab is
    shown; the analog clock and digital display update every 1000ms.
    """

    # ── Palette ────────────────────────────────────────────────────────
    APP_BG       = "#2C1810"
    WOOD_BG      = "#6B3410"
    WOOD_BORDER  = "#A0522D"
    GOLD         = "#D4AF37"
    MUTED_GOLD   = "#8B6914"
    DARK_GOLD    = "#B8860B"
    DARK_WOOD    = "#5C2E0E"
    PANEL_BG     = "#1a0e06"
    PANEL_BORDER = "#5C3A1E"
    DEEP_WOOD    = "#3D1F0A"

    TAB_NAMES = ("RELOJ", "CRONO", "ALARMA", "CUENTA")

    def __init__(self, root: tk.Tk):
        self._root = root
        self._clock_after_id: str | None = None
        self._active_tab = 0

        self._setup_root()
        self._build_layout()
        self._start_clock_loop()

    # ------------------------------------------------------------------
    # Window configuration
    # ------------------------------------------------------------------

    def _setup_root(self):
        self._root.title("Tempus Fugit")
        self._root.configure(bg=self.APP_BG)
        self._root.resizable(False, False)
        # Centre on screen
        self._root.update_idletasks()
        w, h = 360, 640
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self._root.geometry(f"{w}x{h}+{x}+{y}")

    # ------------------------------------------------------------------
    # Full layout assembly
    # ------------------------------------------------------------------

    def _build_layout(self):
        root = self._root

        # ── Outer wood frame ──────────────────────────────────────────
        outer = tk.Frame(root, bg=self.WOOD_BG, bd=3, relief="ridge",
                         highlightbackground=self.WOOD_BORDER,
                         highlightthickness=2)
        outer.pack(fill="both", expand=True, padx=8, pady=8)

        # App title
        tk.Label(
            outer,
            text=" T E M P U S   F U G I T ",
            bg=self.WOOD_BG, fg=self.GOLD,
            font=("Georgia", 13, "bold"),
        ).pack(pady=(10, 2))

        # Decorative separator
        tk.Label(
            outer,
            text="✦ · · ✦ · · ✦",
            bg=self.WOOD_BG, fg=self.MUTED_GOLD,
            font=("Georgia", 9),
        ).pack(pady=(0, 8))

        # ── Clock canvas ──────────────────────────────────────────────
        clock_container = tk.Frame(outer, bg=self.WOOD_BG)
        clock_container.pack()

        self._analog = AnalogClock(clock_container)
        self._analog.pack()

        # ── Digital strip ─────────────────────────────────────────────
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

        # ── Tab bar ───────────────────────────────────────────────────
        tab_bar = tk.Frame(outer, bg=self.PANEL_BG)
        tab_bar.pack(fill="x", padx=0, pady=(8, 0))

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

        # Thin separator under tabs
        tk.Frame(outer, bg=self.PANEL_BORDER, height=1).pack(fill="x")

        # ── Tab content area ──────────────────────────────────────────
        content_area = tk.Frame(outer, bg=self.APP_BG)
        content_area.pack(fill="both", expand=True)

        # RELOJ panel (placeholder; info is in the always-visible area)
        self._reloj_frame = tk.Frame(content_area, bg=self.APP_BG)
        tk.Label(
            self._reloj_frame,
            text="El reloj siempre está activo.",
            bg=self.APP_BG, fg=self.MUTED_GOLD,
            font=("Georgia", 9),
        ).pack(pady=20)
        tk.Label(
            self._reloj_frame,
            text="✦",
            bg=self.APP_BG, fg=self.DARK_GOLD,
            font=("Georgia", 18),
        ).pack()

        # Feature panels
        self._stopwatch = Stopwatch(content_area)
        self._alarm = Alarm(content_area, on_trigger=self._analog.flash_border)
        self._countdown = Countdown(content_area, on_trigger=self._analog.flash_border)

        self._panels = [
            self._reloj_frame,
            self._stopwatch.frame,
            self._alarm.frame,
            self._countdown.frame,
        ]

        # Show the first tab
        self._switch_tab(0)

    # ------------------------------------------------------------------
    # Tab switching
    # ------------------------------------------------------------------

    def _switch_tab(self, index: int):
        # Pause outgoing feature if needed
        if self._active_tab == 1:
            self._stopwatch.stop()
        elif self._active_tab == 2:
            self._alarm.stop()
        elif self._active_tab == 3:
            self._countdown.stop()

        # Hide all panels
        for panel in self._panels:
            panel.pack_forget()

        # Show selected panel
        self._panels[index].pack(fill="both", expand=True)
        self._active_tab = index

        # Style tab buttons
        for i, btn in enumerate(self._tab_btns):
            if i == index:
                btn.config(bg=self.DEEP_WOOD, fg=self.GOLD)
            else:
                btn.config(bg=self.PANEL_BG, fg=self.MUTED_GOLD)

        # Resume outgoing feature if needed
        if index == 1:
            self._stopwatch.resume()
        elif index == 2:
            self._alarm.resume()
        elif index == 3:
            self._countdown.resume()

    # ------------------------------------------------------------------
    # Clock update loop
    # ------------------------------------------------------------------

    def _start_clock_loop(self):
        self._tick_clock()

    def _tick_clock(self):
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
