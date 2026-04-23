import tkinter as tk
from core.config import APP_NAME
from core.theme import BG, CARD, ACCENT, TEXT


class ResultWindow:
    def __init__(self, root, text, x1, x2, sel_y2,
                 close_on_focusout=True,
                 bg_color=BG, alpha=0.95, text_color=TEXT, card_color=CARD):
        win = tk.Toplevel(root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", alpha)
        win.configure(bg=bg_color)

        hdr = tk.Frame(win, bg=card_color)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"  {APP_NAME}",
                 bg=card_color, fg=ACCENT,
                 font=("Segoe UI", 8, "bold")).pack(side="left", pady=5)
        tk.Button(hdr, text="✕", bg=card_color, fg=text_color, relief="flat",
                  font=("Segoe UI", 9), cursor="hand2",
                  command=win.destroy).pack(side="right", padx=6)

        body = tk.Frame(win, bg=bg_color, padx=14, pady=10)
        body.pack()

        box = tk.Text(body, wrap=tk.WORD, font=("Segoe UI", 10), width=50, height=8,
                      bg=bg_color, fg=text_color, relief="flat",
                      selectbackground=ACCENT, selectforeground="#111",
                      insertwidth=0, padx=4, pady=4)
        box.insert("1.0", text)
        box.config(state="disabled")
        box.pack()

        win.update_idletasks()
        w, h = win.winfo_reqwidth(), win.winfo_reqheight()
        cx   = (x1 + x2) // 2
        px   = max(0, min(cx - w // 2, win.winfo_screenwidth() - w))
        py   = sel_y2 + 12
        if py + h > win.winfo_screenheight():
            py = sel_y2 - h - 12
        win.geometry(f"+{px}+{py}")
        win.lift()
        win.update()

        win.focus_force()
        if close_on_focusout:
            win.after(300, lambda: win.bind("<FocusOut>",
                lambda e: win.destroy() if win.winfo_exists() else None))
