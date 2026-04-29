import tkinter as tk
import datetime
import sys


def _beep():
    """winsound on Windows; console bell fallback elsewhere."""
    try:
        import winsound
        winsound.Beep(880, 400)
        winsound.Beep(1100, 400)
        winsound.Beep(880, 400)
    except ImportError:
        print("\a🔔 ALARMA")
        sys.stdout.flush()


class Alarm:
    """Alarm panel. on_trigger callback decouples the flash from the analog clock."""

    BG           = "#2C1810"
    PANEL_BG     = "#1a0e06"
    PANEL_BORDER = "#5C3A1E"
    GOLD         = "#D4AF37"
    MUTED_GOLD   = "#8B6914"
    BTN_BG       = "#3D1F0A"
    BTN_ACTIVE   = "#5C2E0E"
    LABEL_COLOR  = "#5C3A1E"
    RED          = "#8B0000"

    def __init__(self, parent: tk.Widget, on_trigger=None):
        self._after_id: str | None = None
        self._active = False
        self._triggered = False
        self._on_trigger = on_trigger

        self.frame = tk.Frame(parent, bg=self.BG)
        self._build_ui()

    def _build_ui(self):
        f = self.frame

        tk.Label(
            f, text="— alarma —",
            bg=self.BG, fg=self.LABEL_COLOR,
            font=("Georgia", 9),
        ).pack(pady=(10, 4))

        input_frame = tk.Frame(f, bg=self.BG)
        input_frame.pack(pady=8)

        tk.Label(
            input_frame, text="Hora:",
            bg=self.BG, fg=self.MUTED_GOLD,
            font=("Georgia", 11),
        ).grid(row=0, column=0, padx=(0, 6))

        self._hour_var = tk.StringVar(value="07")
        self._min_var = tk.StringVar(value="00")

        spin_cfg = dict(
            width=3,
            font=("Courier New", 14),
            bg="#2C1810", fg=self.GOLD,
            insertbackground=self.GOLD,
            relief="flat",
            buttonbackground="#3D1F0A",
        )

        self._hour_spin = tk.Spinbox(
            input_frame,
            from_=0, to=23, wrap=True,
            textvariable=self._hour_var,
            format="%02.0f",
            **spin_cfg,
        )
        self._hour_spin.grid(row=0, column=1)

        tk.Label(
            input_frame, text=":",
            bg=self.BG, fg=self.GOLD,
            font=("Courier New", 14, "bold"),
        ).grid(row=0, column=2)

        self._min_spin = tk.Spinbox(
            input_frame,
            from_=0, to=59, wrap=True,
            textvariable=self._min_var,
            format="%02.0f",
            **spin_cfg,
        )
        self._min_spin.grid(row=0, column=3)

        self._toggle_btn = tk.Button(
            f, text="ACTIVAR",
            command=self._toggle,
            bg=self.BTN_BG, fg=self.GOLD,
            font=("Georgia", 10, "bold"),
            activebackground=self.BTN_ACTIVE,
            activeforeground=self.GOLD,
            relief="flat", bd=0,
            padx=16, pady=6,
            cursor="hand2",
        )
        self._toggle_btn.pack(pady=10)

        self._status_var = tk.StringVar(value="✦  INACTIVA")
        tk.Label(
            f, textvariable=self._status_var,
            bg=self.BG, fg=self.MUTED_GOLD,
            font=("Georgia", 10),
        ).pack()

        self._scheduled_var = tk.StringVar(value="")
        tk.Label(
            f, textvariable=self._scheduled_var,
            bg=self.BG, fg=self.MUTED_GOLD,
            font=("Courier New", 10),
        ).pack(pady=(4, 0))

    def _toggle(self):
        if self._active:
            self._deactivate()
        else:
            self._activate()

    def _activate(self):
        try:
            h = int(self._hour_var.get())
            m = int(self._min_var.get())
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError
        except ValueError:
            self._status_var.set("⚠  Hora inválida")
            return

        self._active = True
        self._triggered = False
        self._toggle_btn.config(text="DESACTIVAR")
        self._status_var.set("✦  ACTIVA")
        self._scheduled_var.set(f"programada: {h:02d}:{m:02d}")
        self._hour_spin.config(state="disabled")
        self._min_spin.config(state="disabled")
        self._check_alarm()

    def _deactivate(self):
        self._active = False
        if self._after_id:
            self.frame.after_cancel(self._after_id)
            self._after_id = None
        self._toggle_btn.config(text="ACTIVAR")
        self._status_var.set("✦  INACTIVA")
        self._scheduled_var.set("")
        self._hour_spin.config(state="normal")
        self._min_spin.config(state="normal")

    def _check_alarm(self):
        if not self._active:
            return
        now = datetime.datetime.now()
        h = int(self._hour_var.get())
        m = int(self._min_var.get())
        if now.hour == h and now.minute == m and not self._triggered:
            self._triggered = True
            self._fire()
        self._after_id = self.frame.after(1000, self._check_alarm)

    def _fire(self):
        self._status_var.set("🔔  ¡ALARMA!")
        if self._on_trigger:
            self._on_trigger()
        self.frame.after(0, _beep)
        # Deactivate after firing so the alarm doesn't retrigger every second
        self.frame.after(4000, self._deactivate)

    def stop(self):
        if self._after_id:
            self.frame.after_cancel(self._after_id)
            self._after_id = None

    def resume(self):
        if self._active:
            self._check_alarm()
