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
        self._remaining: int = 0
        self._on_trigger = on_trigger

        self.frame = tk.Frame(parent, bg=self.BG)
        self._build_ui()

    def _build_ui(self):
        f = self.frame

        tk.Label(
            f, text="— cuenta regresiva —",
            bg=self.BG, fg=self.LABEL_COLOR,
            font=("Georgia", 9),
        ).pack(pady=(6, 4))

        input_frame = tk.Frame(f, bg=self.BG)
        input_frame.pack(pady=4)

        spin_cfg = dict(
            width=3,
            font=("Courier New", 14),
            bg="#2C1810", fg=self.GOLD,
            insertbackground=self.GOLD,
            relief="flat",
            buttonbackground="#3D1F0A",
        )
        sep_cfg = dict(
            bg=self.BG, fg=self.GOLD,
            font=("Courier New", 16, "bold"),
        )
        lbl_cfg = dict(
            bg=self.BG, fg=self.MUTED_GOLD,
            font=("Georgia", 9),
        )

        tk.Label(input_frame, text="hr",  **lbl_cfg).grid(row=0, column=0)
        tk.Label(input_frame, text="min", **lbl_cfg).grid(row=0, column=2)
        tk.Label(input_frame, text="seg", **lbl_cfg).grid(row=0, column=4)

        self._hr_var = tk.StringVar(value="00")
        self._hr_spin = tk.Spinbox(
            input_frame, from_=0, to=99, wrap=True,
            textvariable=self._hr_var, format="%02.0f", **spin_cfg,
        )
        self._hr_spin.grid(row=1, column=0, padx=3)

        tk.Label(input_frame, text=":", **sep_cfg).grid(row=1, column=1)

        self._min_var = tk.StringVar(value="05")
        self._min_spin = tk.Spinbox(
            input_frame, from_=0, to=59, wrap=True,
            textvariable=self._min_var, format="%02.0f", **spin_cfg,
        )
        self._min_spin.grid(row=1, column=2, padx=3)

        tk.Label(input_frame, text=":", **sep_cfg).grid(row=1, column=3)

        self._sec_var = tk.StringVar(value="00")
        self._sec_spin = tk.Spinbox(
            input_frame, from_=0, to=59, wrap=True,
            textvariable=self._sec_var, format="%02.0f", **spin_cfg,
        )
        self._sec_spin.grid(row=1, column=4, padx=3)

        self._error_lbl = tk.Label(
            f, text="",
            bg=self.BG, fg="#FF5555",
            font=("Georgia", 8),
        )

        self._display_var = tk.StringVar(value="00:05:00")
        self._display_lbl = tk.Label(
            f, textvariable=self._display_var,
            bg=self.PANEL_BG, fg=self.DARK_GOLD,
            font=("Courier New", 22),
            relief="flat", bd=0,
            padx=20, pady=4,
        )
        self._display_lbl.pack(pady=(6, 6))

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
            command=self._toggle_start, **btn_cfg,
        )
        self._start_btn.grid(row=0, column=0, padx=5)

        self._reset_btn = tk.Button(
            btn_frame, text="RESET",
            command=self._reset,
            state="disabled", **btn_cfg,
        )
        self._reset_btn.grid(row=0, column=1, padx=5)

    def _show_error(self, msg: str):
        self._error_lbl.config(text=msg)
        self._error_lbl.pack(before=self._display_lbl, pady=(2, 0))
        self.frame.after(1500, self._hide_error)

    def _hide_error(self):
        self._error_lbl.pack_forget()

    def _toggle_start(self):
        if not self._running:
            if self._remaining == 0:
                try:
                    h = int(self._hr_var.get().strip() or "0")
                    m = int(self._min_var.get().strip() or "0")
                    s = int(self._sec_var.get().strip() or "0")
                    if not (0 <= h <= 99 and 0 <= m <= 59 and 0 <= s <= 59):
                        raise ValueError
                    total = h * 3600 + m * 60 + s
                    if total == 0:
                        self._show_error("⚠  Ingresa un tiempo mayor a 0")
                        return
                    self._remaining = total
                except ValueError:
                    self._show_error("⚠  Tiempo inválido")
                    return
            self._error_lbl.pack_forget()
            self._running = True
            self._start_btn.config(text="PAUSAR")
            self._reset_btn.config(state="disabled")
            self._hr_spin.config(state="disabled")
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
        self._hr_spin.config(state="normal")
        self._min_spin.config(state="normal")
        self._sec_spin.config(state="normal")
        try:
            h = int(self._hr_var.get().strip() or "0")
            m = int(self._min_var.get().strip() or "0")
            s = int(self._sec_var.get().strip() or "0")
            self._display_var.set(f"{h:02d}:{m:02d}:{s:02d}")
        except ValueError:
            self._display_var.set("00:00:00")

    def _tick(self):
        if not self._running:
            return
        if self._remaining <= 0:
            self._running = False
            self._display_var.set("00:00:00")
            self._start_btn.config(text="INICIAR")
            self._reset_btn.config(state="normal")
            self._hr_spin.config(state="normal")
            self._min_spin.config(state="normal")
            self._sec_spin.config(state="normal")
            if self._on_trigger:
                self._on_trigger()
            self.frame.after(0, _beep)
            return
        hrs  = self._remaining // 3600
        mins = (self._remaining % 3600) // 60
        secs = self._remaining % 60
        self._display_var.set(f"{hrs:02d}:{mins:02d}:{secs:02d}")
        self._remaining -= 1
        self._after_id = self.frame.after(1000, self._tick)

    def stop(self):
        if self._running and self._after_id:
            self.frame.after_cancel(self._after_id)
            self._after_id = None

    def resume(self):
        if self._running:
            self._tick()
