import tkinter as tk
from core.config import APP_NAME
from core.theme import ACCENT
from core.i18n import t


class DragOverlay:
    def __init__(self, root, callback):
        self._root    = root
        self.callback = callback
        self.start_x  = self.start_y = 0
        self.rect     = None

        self.win = tk.Toplevel(root)
        self.win.attributes("-fullscreen", True)
        self.win.attributes("-alpha", 0.2)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="#000000")
        self.win.config(cursor="crosshair")

        self.canvas = tk.Canvas(self.win, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        tk.Label(self.canvas,
                 text=f"{APP_NAME}  |  {t('overlay_hint')}",
                 bg="#000000", fg=ACCENT, font=("Segoe UI", 10)
                 ).place(relx=0.5, rely=0.03, anchor="n")

        self.canvas.bind("<ButtonPress-1>",  self._press)
        self.canvas.bind("<B1-Motion>",      self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.canvas.bind("<Escape>", lambda e: self.win.destroy())
        self.win.bind("<Escape>",    lambda e: self.win.destroy())
        self.canvas.focus_set()

    def _press(self, e):
        self.start_x, self.start_y = e.x, e.y

    def _drag(self, e):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, e.x, e.y,
            outline=ACCENT, width=2
        )

    def _release(self, e):
        x1 = min(self.start_x, e.x)
        y1 = min(self.start_y, e.y)
        x2 = max(self.start_x, e.x)
        y2 = max(self.start_y, e.y)
        self.win.destroy()
        if x2 - x1 > 10 or y2 - y1 > 10:
            self._root.after(150, lambda: self.callback(x1, y1, x2, y2))
