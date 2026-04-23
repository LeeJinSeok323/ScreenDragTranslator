import tkinter as tk
from core.theme import CARD, ACCENT
from core.i18n import t


class LoadingIndicator:
    def __init__(self, root, x1, x2, sel_y2,
                 card_color=CARD, alpha=0.88, text_color=ACCENT):
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", alpha)
        self.win.configure(bg=card_color)

        self.label = tk.Label(self.win, text=f"{t('loading_text')}  ·",
                              bg=card_color, fg=text_color,
                              font=("Segoe UI", 10))
        self.label.pack(padx=16, pady=8)

        self.win.update_idletasks()
        w  = self.win.winfo_reqwidth()
        cx = (x1 + x2) // 2
        px = max(0, cx - w // 2)
        py = sel_y2 + 12
        if py + 40 > self.win.winfo_screenheight():
            py = sel_y2 - 50
        self.win.geometry(f"+{px}+{py}")
        self.win.lift()
        self.win.update()

        self._dots = 0
        self._animate()

    def _animate(self):
        if not self.win.winfo_exists():
            return
        self._dots = (self._dots % 3) + 1
        self.label.config(text=f"{t('loading_text')}  {'·' * self._dots}")
        self.win.after(400, self._animate)

    def close(self):
        if self.win.winfo_exists():
            self.win.destroy()
