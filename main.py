"""main.py — Entry point for Tempus Fugit desktop clock application."""

import tkinter as tk
from ui.app_window import AppWindow


def main():
    root = tk.Tk()
    app = AppWindow(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.destroy(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
