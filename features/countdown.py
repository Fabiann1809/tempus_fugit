"""countdown.py — Countdown timer feature."""

import tkinter as tk
import sys


def _beep():
    try:
        import winsound
        for _ in range(3):
            winsound.Beep(1200, 300)
    except ImportError:
        print("\a🔔 FIN")
        sys.stdout.flush()


class Countdown:
    """
    Countdown timer panel.

    The user sets minutes and seconds via Spinbox inputs, then starts the
    countdown.  When it reaches 00:00 the clock face flashes and a beep
    plays via the on_trigger callback.

    State machine: idle → running → paused → running | idle (reset)
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

    def __init__(self, parent: tk.Widget, on_trigger=None):
        self._after_id: str | None = None
        self._running = False
        self._remaining: int = 0        # seconds remaining
        self._on_trigger = on_trigger   # callable() → flash clock face

        self.frame = tk.Frame(parent, bg=self.BG)
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        f = self.frame

        # Section label
        tk.Label(
            f, text="— cuenta regresiva —",
            bg=self.BG, fg=self.LABEL_COLOR,
            font=("Georgia", 9),
        ).pack(pady=(10, 4))

        # Input row: MM  :  SS
        input_frame = tk.Frame(f, bg=self.BG)
        input_frame.pack(pady=6)

        spin_cfg = dict(
            width=4,
            font=("Courier New", 16),
            bg="#2C1810", fg=self.GOLD,
            insertbackground=self.GOLD,
            relief="flat",
            buttonbackground="#3D1F0A",
        )

        tk.Label(
            input_frame, text="min",
            bg=self.BG, fg=self.MUTED_GOLD,
            font=("Georgia", 9),
        ).grid(row=0, column=0)

        self._min_var = tk.StringVar(value="05")
        self._min_spin = tk.Spinbox(
            input_frame,
            from_=0, to=99, wrap=True,
            textvariable=self._min_var,
            format="%02.0f",
            **spin_cfg,
        )
        self._min_spin.grid(row=1, column=0, padx=4)

        tk.Label(
            input_frame, text=":",
            bg=self.BG, fg=self.GOLD,
            font=("Courier New", 18, "bold"),
        ).grid(row=1, column=1)

        tk.Label(
            input_frame, text="seg",
            bg=self.BG, fg=self.MUTED_GOLD,
            font=("Georgia", 9),
        ).grid(row=0, column=2)

        self._sec_var = tk.StringVar(value="00")
        self._sec_spin = tk.Spinbox(
            input_frame,
            from_=0, to=59, wrap=True,
            textvariable=self._sec_var,
            format="%02.0f",
            **spin_cfg,
        )
        self._sec_spin.grid(row=1, column=2, padx=4)

        # Countdown display
        self._display_var = tk.StringVar(value="05:00")
        tk.Label(
            f, textvariable=self._display_var,
            bg=self.PANEL_BG, fg=self.DARK_GOLD,
            font=("Courier New", 28),
            relief="flat", bd=0,
            padx=20, pady=6,
        ).pack(pady=(8, 8))

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
            btn_frame, text="INICIAR",
            command=self._toggle_start, **btn_cfg
        )
        self._start_btn.grid(row=0, column=0, padx=5)

        self._reset_btn = tk.Button(
            btn_frame, text="RESET",
            command=self._reset,
            state="disabled", **btn_cfg
        )
        self._reset_btn.grid(row=0, column=1, padx=5)

    # ------------------------------------------------------------------
    # Button callbacks
    # ------------------------------------------------------------------

    def _toggle_start(self):
        if not self._running:
            if self._remaining == 0:
                # Load from spinboxes
                try:
                    m = int(self._min_var.get())
                    s = int(self._sec_var.get())
                    total = m * 60 + s
                    if total == 0:
                        return
                    self._remaining = total
                except ValueError:
                    return
            self._running = True
            self._start_btn.config(text="PAUSAR")
            self._reset_btn.config(state="disabled")
            self._min_spin.config(state="disabled")
            self._sec_spin.config(state="disabled")
            self._tick()
        else:
            self._running = False
            if self._after_id:
                self.frame.after_cancel(self._after_id)
                self._after_id = None
            self._start_btn.config(text="INICIAR")
            self._reset_btn.config(state="normal")

    def _reset(self):
        self._running = False
        if self._after_id:
            self.frame.after_cancel(self._after_id)
            self._after_id = None
        self._remaining = 0
        self._start_btn.config(text="INICIAR")
        self._reset_btn.config(state="disabled")
        self._min_spin.config(state="normal")
        self._sec_spin.config(state="normal")
        # Restore display from spinboxes
        try:
            m = int(self._min_var.get())
            s = int(self._sec_var.get())
            self._display_var.set(f"{m:02d}:{s:02d}")
        except ValueError:
            self._display_var.set("00:00")

    # ------------------------------------------------------------------
    # Tick loop (1-second interval)
    # ------------------------------------------------------------------

    def _tick(self):
        if not self._running:
            return
        if self._remaining <= 0:
            self._running = False
            self._display_var.set("00:00")
            self._start_btn.config(text="INICIAR")
            self._reset_btn.config(state="normal")
            self._min_spin.config(state="normal")
            self._sec_spin.config(state="normal")
            if self._on_trigger:
                self._on_trigger()
            self.frame.after(0, _beep)
            return
        mins = self._remaining // 60
        secs = self._remaining % 60
        self._display_var.set(f"{mins:02d}:{secs:02d}")
        self._remaining -= 1
        self._after_id = self.frame.after(1000, self._tick)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def stop(self):
        if self._running and self._after_id:
            self.frame.after_cancel(self._after_id)
            self._after_id = None

    def resume(self):
        if self._running:
            self._tick()
