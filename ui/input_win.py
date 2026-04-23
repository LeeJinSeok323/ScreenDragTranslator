import tkinter as tk
import threading

from core.config import APP_NAME
from core.theme import BG, CARD, ACCENT, TEXT, MUTED
from core.i18n import t

_TARGET_LANGS = [("EN", "en"), ("ID", "id"), ("ES", "es"), ("KO", "ko")]


class InputWindow:
    def __init__(self, root, translate_fn, theme=None, default_target="en"):
        th     = theme or {}
        bg     = th.get("bg",     BG)
        card   = th.get("card",   CARD)
        accent = th.get("accent", ACCENT)
        text   = th.get("text",   TEXT)
        muted  = th.get("muted",  MUTED)
        alpha  = th.get("alpha",  0.96)

        self._translate_fn = translate_fn
        self._busy         = False
        self._accent       = accent
        self._muted        = muted
        self._card         = card
        self._target_lang  = default_target
        self._lang_btns    = {}

        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", alpha)
        self.win.configure(bg=bg)

        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        w, h = 480, 160
        self.win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        hdr = tk.Frame(self.win, bg=card)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"  {APP_NAME}",
                 bg=card, fg=accent, font=("Segoe UI", 8, "bold")).pack(side="left", pady=6)
        tk.Button(hdr, text="✕", bg=card, fg=muted, relief="flat",
                  font=("Segoe UI", 9), cursor="hand2",
                  command=self.win.destroy).pack(side="right", padx=6)

        body = tk.Frame(self.win, bg=bg)
        body.pack(fill="x", padx=16, pady=(10, 0))

        lang_row = tk.Frame(body, bg=bg)
        lang_row.pack(anchor="w", pady=(0, 8))
        tk.Label(lang_row, text=t("input_auto_src"),
                 bg=bg, fg=muted, font=("Segoe UI", 8)).pack(side="left", padx=(0, 6))
        for code, lang_code in _TARGET_LANGS:
            btn = tk.Button(
                lang_row, text=code,
                font=("Segoe UI", 8, "bold"),
                relief="flat", cursor="hand2",
                padx=8, pady=2,
                command=lambda lc=lang_code: self._set_target(lc),
            )
            btn.pack(side="left", padx=2)
            self._lang_btns[lang_code] = btn
        self._update_lang_btns()

        self.entry = tk.Entry(body, font=("Segoe UI", 11), bg=card, fg=text,
                              relief="flat", insertbackground=accent, bd=0,
                              disabledbackground=muted, disabledforeground="#333333")
        self.entry.pack(fill="x", ipady=8)
        self.entry.focus_force()

        self.hint = tk.Label(self.win, text=t("input_hint"),
                             bg=bg, fg=muted, font=("Segoe UI", 8))
        self.hint.pack(anchor="w", padx=16, pady=(6, 0))

        self.entry.bind("<Return>", self._translate)
        self.win.bind("<Escape>", lambda e: self.win.destroy())

    def _set_target(self, lang_code):
        self._target_lang = lang_code
        self._update_lang_btns()

    def _update_lang_btns(self):
        for lc, btn in self._lang_btns.items():
            if lc == self._target_lang:
                btn.config(bg=self._accent, fg="#111")
            else:
                btn.config(bg=self._card, fg=self._muted)

    def _translate(self, e=None):
        if self._busy:
            return
        text = self.entry.get().strip()
        if not text:
            return
        self._busy = True
        self.entry.config(state="disabled")
        self.hint.config(text=t("translating"), fg=self._accent)
        self.win.update()

        target = self._target_lang

        def do():
            try:
                result = self._translate_fn(text, target)
                self.win.clipboard_clear()
                self.win.clipboard_append(result)
                self.win.after(0, self.win.destroy)
            except Exception as ex:
                err_msg = str(ex)

                def on_err():
                    self._busy = False
                    self.entry.config(state="normal")
                    self.hint.config(text=f"{t('error_prefix')}{err_msg}", fg="#ff6b6b")

                self.win.after(0, on_err)

        threading.Thread(target=do, daemon=True).start()
