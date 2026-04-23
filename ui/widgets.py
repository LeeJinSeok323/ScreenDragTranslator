import tkinter as tk
from core.theme import BG, CARD, ACCENT, MUTED
from core.i18n import t

_MOD_KEYS = {
    "shift_l", "shift_r", "control_l", "control_r", "alt_l", "alt_r",
    "caps_lock", "num_lock", "scroll_lock", "super_l", "super_r", "menu"
}


def sep(parent):
    tk.Frame(parent, bg=MUTED, height=1).pack(fill="x", padx=20, pady=8)


def styled_win(root, w, h, title="", topmost=True):
    win = tk.Toplevel(root)
    win.configure(bg=BG)
    win.resizable(False, False)
    win.attributes("-topmost", topmost)
    if title:
        win.title(title)
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    return win


def _build_combo(event):
    mods = []
    if event.state & 0x4:      mods.append("ctrl")
    if event.state & 0x1:      mods.append("shift")
    if event.state & 0x20000:  mods.append("alt")
    key = event.keysym.lower()
    if key in _MOD_KEYS:
        return None
    return "+".join(mods + [key])


class HotkeyEntry:
    def __init__(self, parent, default_val):
        self._var       = tk.StringVar(value=default_val)
        self._original  = default_val
        self._default   = default_val
        self._capturing = False

        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x", padx=20, pady=(0, 2))

        self._entry = tk.Entry(frame, textvariable=self._var,
                               font=("Segoe UI", 9), bg=CARD, fg=ACCENT,
                               relief="flat", insertbackground=ACCENT,
                               bd=0, state="readonly", cursor="hand2",
                               readonlybackground=CARD)
        self._entry.pack(side="left", expand=True, fill="x", ipady=6, padx=(0, 6))

        tk.Button(frame, text=t("reset"), font=("Segoe UI", 8),
                  bg=CARD, fg=MUTED, relief="flat", cursor="hand2",
                  command=self._reset).pack(side="left", ipady=6, padx=2)

        self._entry.bind("<FocusIn>",  self._on_focus)
        self._entry.bind("<FocusOut>", self._on_blur)
        self._entry.bind("<KeyPress>", self._on_key)
        self._entry.bind("<Button-1>", lambda e: self._entry.focus_set())

    def _on_focus(self, e):
        self._capturing = True
        self._var.set(t("hotkey_press"))
        self._entry.config(fg=MUTED)

    def _on_blur(self, e):
        self._capturing = False
        self._var.set(self._default)
        self._entry.config(fg=ACCENT)

    def _on_key(self, e):
        combo = _build_combo(e)
        if combo:
            self._default = combo
            self._var.set(combo)
            self._capturing = False
            self._entry.config(fg=ACCENT)
            self._entry.master.focus_set()
        return "break"

    def _reset(self):
        self._default = self._original
        self._var.set(self._original)

    def get(self):
        return self._default
