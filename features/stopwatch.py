"""stopwatch.py — Stopwatch feature with ClockMemory lap tracking."""

import tkinter as tk
import datetime
from data_structures.clock_memory import ClockMemory, TimeRecord
from utils.time_helpers import format_stopwatch


class Stopwatch:
    """
    Stopwatch panel with centisecond precision and ClockMemory lap storage.

    State machine:
        idle  →  running  →  paused  →  running  …
        any state → reset → idle

    Laps are stored as TimeRecord nodes in a ClockMemory circular doubly
    linked list.  The user can scroll the lap list forward and backward
    using the two navigation buttons, which call replay_forward() and
    replay_backward() on the list.
    """

    # ── Palette ────────────────────────────────────────────────────────
    BG           = "#2C1810"
    PANEL_BG     = "#1a0e06"
    PANEL_BORDER = "#5C3A1E"
    GOLD         = "#D4AF37"
    MUTED_GOLD   = "#8B6914"
    DARK_GOLD    = "#C9922A"
    BTN_BG       = "#3D1F0A"
    BTN_ACTIVE   = "#5C2E0E"
    LABEL_COLOR  = "#5C3A1E"

    def __init__(self, parent: tk.Widget):
        self._after_id: str | None = None
        self._running = False
        self._centiseconds = 0          # accumulated centiseconds
        self._start_epoch: float = 0.0  # time.monotonic() reference

        self._memory = ClockMemory()
        self._current_node: TimeRecord | None = None

        self.frame = tk.Frame(parent, bg=self.BG)
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        f = self.frame

        # Section label
        tk.Label(
            f, text="— cronómetro —",
            bg=self.BG, fg=self.LABEL_COLOR,
            font=("Georgia", 9),
        ).pack(pady=(8, 2))

        # Main time display
        self._display_var = tk.StringVar(value="00:00.00")
        tk.Label(
            f, textvariable=self._display_var,
            bg=self.PANEL_BG, fg=self.DARK_GOLD,
            font=("Courier New", 28),
            relief="flat", bd=0,
            padx=20, pady=6,
        ).pack(pady=(4, 8))

        # Buttons row
        btn_frame = tk.Frame(f, bg=self.BG)
        btn_frame.pack(pady=4)

        btn_cfg = dict(
            bg=self.BTN_BG, fg=self.GOLD,
            font=("Georgia", 10, "bold"),
            activebackground=self.BTN_ACTIVE,
            activeforeground=self.GOLD,
            relief="flat", bd=0,
            padx=14, pady=5,
            cursor="hand2",
        )

        self._start_btn = tk.Button(
            btn_frame, text="INICIAR", command=self._toggle_start, **btn_cfg
        )
        self._start_btn.grid(row=0, column=0, padx=5)

        self._lap_btn = tk.Button(
            btn_frame, text="LAP", command=self._record_lap,
            state="disabled", **btn_cfg
        )
        self._lap_btn.grid(row=0, column=1, padx=5)

        self._reset_btn = tk.Button(
            btn_frame, text="RESET", command=self._reset,
            state="disabled", **btn_cfg
        )
        self._reset_btn.grid(row=0, column=2, padx=5)

        # Lap history panel
        lap_outer = tk.Frame(f, bg=self.PANEL_BORDER, bd=1)
        lap_outer.pack(fill="both", expand=True, padx=12, pady=(8, 4))

        lap_inner = tk.Frame(lap_outer, bg=self.PANEL_BG)
        lap_inner.pack(fill="both", expand=True, padx=1, pady=1)

        # Navigation row
        nav_frame = tk.Frame(lap_inner, bg=self.PANEL_BG)
        nav_frame.pack(fill="x", padx=6, pady=(4, 0))

        nav_btn_cfg = dict(
            bg=self.BTN_BG, fg=self.GOLD,
            font=("Georgia", 10, "bold"),
            activebackground=self.BTN_ACTIVE,
            activeforeground=self.GOLD,
            relief="flat", bd=0,
            padx=10, pady=3,
            cursor="hand2",
        )
        tk.Button(
            nav_frame, text="◀", command=self._nav_backward, **nav_btn_cfg
        ).pack(side="left")
        tk.Button(
            nav_frame, text="▶", command=self._nav_forward, **nav_btn_cfg
        ).pack(side="right")
        tk.Label(
            nav_frame, text="VUELTAS",
            bg=self.PANEL_BG, fg=self.MUTED_GOLD,
            font=("Georgia", 8),
        ).pack(side="left", expand=True)

        # Scrollable text box for laps
        self._lap_text = tk.Text(
            lap_inner,
            bg=self.PANEL_BG, fg=self.MUTED_GOLD,
            font=("Courier New", 10),
            relief="flat", bd=0,
            height=6,
            state="disabled",
            cursor="arrow",
        )
        self._lap_text.pack(fill="both", expand=True, padx=6, pady=(2, 6))
        self._lap_text.tag_config("highlight", foreground=self.GOLD)

    # ------------------------------------------------------------------
    # Button callbacks
    # ------------------------------------------------------------------

    def _toggle_start(self):
        import time as _time
        if not self._running:
            self._running = True
            self._start_epoch = _time.monotonic() - self._centiseconds / 100.0
            self._start_btn.config(text="PAUSAR")
            self._lap_btn.config(state="normal")
            self._reset_btn.config(state="disabled")
            self._tick()
        else:
            self._running = False
            if self._after_id:
                self.frame.after_cancel(self._after_id)
                self._after_id = None
            self._start_btn.config(text="INICIAR")
            self._lap_btn.config(state="disabled")
            self._reset_btn.config(state="normal")

    def _record_lap(self):
        if not self._running:
            return
        lap_num = len(self._memory) + 1
        time_str = format_stopwatch(self._centiseconds)
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        node = self._memory.record_moment(lap_num, time_str, now_str)
        self._current_node = node
        self._refresh_lap_display()

    def _reset(self):
        self._running = False
        if self._after_id:
            self.frame.after_cancel(self._after_id)
            self._after_id = None
        self._centiseconds = 0
        self._memory.clear()
        self._current_node = None
        self._display_var.set("00:00.00")
        self._start_btn.config(text="INICIAR")
        self._lap_btn.config(state="disabled")
        self._reset_btn.config(state="disabled")
        self._refresh_lap_display()

    def _nav_forward(self):
        if self._current_node is None and self._memory:
            self._current_node = self._memory.first_record
        elif self._current_node is not None and self._memory:
            self._current_node = self._memory.replay_forward(self._current_node)
        self._refresh_lap_display()

    def _nav_backward(self):
        if self._current_node is None and self._memory:
            self._current_node = self._memory.first_record
        elif self._current_node is not None and self._memory:
            self._current_node = self._memory.replay_backward(self._current_node)
        self._refresh_lap_display()

    # ------------------------------------------------------------------
    # Timer tick (10ms interval)
    # ------------------------------------------------------------------

    def _tick(self):
        if not self._running:
            return
        import time as _time
        elapsed = _time.monotonic() - self._start_epoch
        self._centiseconds = int(elapsed * 100)
        self._display_var.set(format_stopwatch(self._centiseconds))
        self._after_id = self.frame.after(10, self._tick)

    # ------------------------------------------------------------------
    # Lap display
    # ------------------------------------------------------------------

    def _refresh_lap_display(self):
        records = self._memory.all_records()
        self._lap_text.config(state="normal")
        self._lap_text.delete("1.0", "end")

        for rec in records:
            label = f"  Vuelta {rec.lap_number:>2}   {rec.elapsed_time_str}   {rec.timestamp}\n"
            if rec is self._current_node:
                self._lap_text.insert("end", label, "highlight")
            else:
                self._lap_text.insert("end", label)

        self._lap_text.config(state="disabled")
        # Scroll to highlighted node
        if records and self._current_node:
            idx = next(
                (i for i, r in enumerate(records) if r is self._current_node), None
            )
            if idx is not None:
                self._lap_text.see(f"{idx + 1}.0")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def stop(self):
        """Pause the tick loop when the tab is hidden."""
        if self._running and self._after_id:
            self.frame.after_cancel(self._after_id)
            self._after_id = None

    def resume(self):
        """Restart the tick loop when the tab becomes visible again."""
        if self._running:
            import time as _time
            self._start_epoch = _time.monotonic() - self._centiseconds / 100.0
            self._tick()
