import tkinter as tk
import datetime
import sys


def _beep(stop_fn=None):
    """Play alarm tones, checking stop_fn() between each tone so dismiss is near-instant."""
    try:
        import winsound
        for freq, ms in [(880, 250), (1100, 250), (880, 250)]:
            if stop_fn and stop_fn():
                return
            winsound.Beep(freq, ms)
    except ImportError:
        if not (stop_fn and stop_fn()):
            print("\a🔔 ALARMA")
            sys.stdout.flush()


class Alarm:

    BG           = "#2C1810"
    PANEL_BG     = "#1a0e06"
    PANEL_BORDER = "#5C3A1E"
    GOLD         = "#D4AF37"
    MUTED_GOLD   = "#8B6914"
    BTN_BG       = "#3D1F0A"
    BTN_ACTIVE   = "#5C2E0E"
    LABEL_COLOR  = "#5C3A1E"
    RED          = "#8B0000"

    def __init__(self, parent: tk.Widget, on_trigger=None,
                 on_dismiss_needed=None, get_time=None):
        self._on_trigger = on_trigger
        self._on_dismiss_needed = on_dismiss_needed
        self._get_time = get_time          # callable → datetime; falls back to now()
        self._alarms: list[dict] = []
        self._after_id: str | None = None

        self.frame = tk.Frame(parent, bg=self.BG)
        self._build_ui()
        self._check_loop()  # starts immediately and never stops

    def _build_ui(self):
        f = self.frame

        tk.Label(
            f, text="— alarma —",
            bg=self.BG, fg=self.LABEL_COLOR,
            font=("Georgia", 9),
        ).pack(pady=(8, 4))

        # Input row: HH : MM + add button
        add_frame = tk.Frame(f, bg=self.BG)
        add_frame.pack(pady=(0, 6))

        spin_cfg = dict(
            width=3,
            font=("Courier New", 13),
            bg=self.PANEL_BG, fg=self.GOLD,
            insertbackground=self.GOLD,
            relief="flat",
            buttonbackground=self.BTN_BG,
        )

        self._hour_var = tk.StringVar(value="07")
        tk.Spinbox(
            add_frame, from_=0, to=23, wrap=True,
            textvariable=self._hour_var, format="%02.0f",
            **spin_cfg,
        ).pack(side="left")

        tk.Label(add_frame, text=":", bg=self.BG, fg=self.GOLD,
                 font=("Courier New", 13, "bold")).pack(side="left", padx=2)

        self._min_var = tk.StringVar(value="00")
        tk.Spinbox(
            add_frame, from_=0, to=59, wrap=True,
            textvariable=self._min_var, format="%02.0f",
            **spin_cfg,
        ).pack(side="left")

        tk.Button(
            add_frame, text="+ AGREGAR",
            command=self._add_alarm,
            bg=self.BTN_BG, fg=self.GOLD,
            font=("Georgia", 9, "bold"),
            activebackground=self.BTN_ACTIVE,
            activeforeground=self.GOLD,
            relief="flat", bd=0,
            padx=10, pady=4,
            cursor="hand2",
        ).pack(side="left", padx=(10, 0))

        # Alarm list
        list_outer = tk.Frame(f, bg=self.PANEL_BORDER, bd=1)
        list_outer.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        self._list_frame = tk.Frame(list_outer, bg=self.PANEL_BG)
        self._list_frame.pack(fill="both", expand=True, padx=1, pady=1)

        self._empty_lbl = tk.Label(
            self._list_frame,
            text="No hay alarmas registradas.",
            bg=self.PANEL_BG, fg=self.MUTED_GOLD,
            font=("Georgia", 9),
        )
        self._empty_lbl.pack(pady=14)

    # ── Alarm management ───────────────────────────────────────────────

    def _add_alarm(self):
        try:
            h = int(self._hour_var.get())
            m = int(self._min_var.get())
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError
        except ValueError:
            return

        self._empty_lbl.pack_forget()

        alarm: dict = {
            "hour": h, "minute": m,
            "active": True, "triggered": False,
        }

        row = tk.Frame(self._list_frame, bg=self.PANEL_BG)
        row.pack(fill="x", padx=4, pady=2)

        tk.Label(
            row, text=f"{h:02d}:{m:02d}",
            bg=self.PANEL_BG, fg=self.GOLD,
            font=("Courier New", 13, "bold"),
        ).pack(side="left", padx=(8, 10))

        status_var = tk.StringVar(value="✦ ACTIVA")
        alarm["status_var"] = status_var
        tk.Label(
            row, textvariable=status_var,
            bg=self.PANEL_BG, fg=self.MUTED_GOLD,
            font=("Georgia", 8),
            width=12, anchor="w",
        ).pack(side="left")

        small_btn = dict(
            font=("Georgia", 8, "bold"),
            bg=self.BTN_BG, fg=self.GOLD,
            activebackground=self.BTN_ACTIVE,
            activeforeground=self.GOLD,
            relief="flat", bd=0,
            padx=6, pady=2,
            cursor="hand2",
        )

        toggle_btn = tk.Button(
            row, text="OFF",
            command=lambda a=alarm: self._toggle_alarm(a),
            **small_btn,
        )
        toggle_btn.pack(side="left", padx=4)
        alarm["toggle_btn"] = toggle_btn

        tk.Button(
            row, text="✕",
            command=lambda r=row, a=alarm: self._delete_alarm(r, a),
            **small_btn,
        ).pack(side="right", padx=(4, 8))

        alarm["row"] = row
        self._alarms.append(alarm)

    def _toggle_alarm(self, alarm: dict):
        alarm["active"] = not alarm["active"]
        alarm["triggered"] = False
        if alarm["active"]:
            alarm["status_var"].set("✦ ACTIVA")
            alarm["toggle_btn"].config(text="OFF")
        else:
            alarm["status_var"].set("✦ INACTIVA")
            alarm["toggle_btn"].config(text="ON")

    def _delete_alarm(self, row: tk.Frame, alarm: dict):
        self._alarms.remove(alarm)
        row.destroy()
        if not self._alarms:
            self._empty_lbl.pack(pady=14)

    # ── Check loop — always running, tab-independent ───────────────────

    def _check_loop(self):
        now = self._get_time() if self._get_time else datetime.datetime.now()
        for alarm in self._alarms:
            at_alarm_time = (now.hour == alarm["hour"]
                             and now.minute == alarm["minute"])
            # Auto-reset triggered when displayed time has left the alarm minute
            if alarm["triggered"] and not at_alarm_time:
                alarm["triggered"] = False
            if alarm["active"] and not alarm["triggered"] and at_alarm_time:
                alarm["triggered"] = True
                self._fire(alarm)
        self._after_id = self.frame.after(1000, self._check_loop)

    def _fire(self, alarm: dict):
        alarm["status_var"].set("🔔 ¡ALARMA!")
        alarm["beeping"] = True
        if self._on_trigger:
            self._on_trigger()
        self._repeat_beep(alarm)
        if self._on_dismiss_needed:
            self._on_dismiss_needed(lambda a=alarm: self._dismiss(a))

    def _repeat_beep(self, alarm: dict):
        if not alarm.get("beeping"):
            return
        import threading
        threading.Thread(
            target=_beep,
            kwargs={"stop_fn": lambda: not alarm.get("beeping")},
            daemon=True,
        ).start()
        alarm["beep_after"] = self.frame.after(3500, lambda: self._repeat_beep(alarm))

    def _dismiss(self, alarm: dict):
        alarm["beeping"] = False
        if alarm.get("beep_after"):
            self.frame.after_cancel(alarm["beep_after"])
            alarm["beep_after"] = None
        alarm["status_var"].set("✦ ACTIVA" if alarm["active"] else "✦ INACTIVA")
        # triggered resets automatically in _check_loop once the displayed
        # time moves away from the alarm minute, so no manual reset needed

    # ── Lifecycle (alarm loop is tab-independent, nothing to stop) ─────

    def stop(self):
        pass

    def resume(self):
        pass
