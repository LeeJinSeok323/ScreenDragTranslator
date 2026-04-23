import os
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk

from core.config import (APP_NAME, MODEL, MODELS, HOTKEY, HOTKEY_EN,
                          save_config, set_autostart)
from core.theme import (BG, CARD, ACCENT, TEXT, MUTED,
                         THEME_PRESETS, theme_text, theme_card)
from core.i18n import t, load as i18n_load, LANG_OPTIONS, LANG_CODES
from ui.widgets import sep, styled_win, HotkeyEntry


class SettingsWindow:
    def __init__(self, root, config, on_save, on_close=None, first_run=False):
        self.config  = config
        self.on_save = on_save

        win = styled_win(root, 540, 440, APP_NAME)
        self._win = win
        win.grab_set()
        if first_run:
            win.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))
        win.bind("<Destroy>", lambda e: on_close() if on_close and e.widget is win else None)

        P = 20

        self._style = ttk.Style()
        self._style.theme_use("clam")
        self._style.configure("Dark.TNotebook", background=BG, borderwidth=0)
        self._style.configure("Dark.TNotebook.Tab",
                              background=CARD, foreground=MUTED,
                              padding=[16, 7], font=("Segoe UI", 9))
        self._style.map("Dark.TNotebook.Tab",
                        background=[("selected", BG)],
                        foreground=[("selected", ACCENT)])
        self._style.configure("Dark.TCombobox",
                              fieldbackground=CARD, background=CARD,
                              foreground=TEXT, selectbackground=CARD,
                              selectforeground=ACCENT, arrowcolor=ACCENT,
                              bordercolor=MUTED, lightcolor=CARD, darkcolor=CARD)
        self._style.map("Dark.TCombobox",
                        fieldbackground=[("readonly", CARD)],
                        foreground=[("readonly", TEXT)])

        nb = ttk.Notebook(win, style="Dark.TNotebook")
        nb.pack(fill="both", expand=True)

        t_basic  = tk.Frame(nb, bg=BG)
        t_hotkey = tk.Frame(nb, bg=BG)
        t_theme  = tk.Frame(nb, bg=BG)
        t_gen    = tk.Frame(nb, bg=BG)
        nb.add(t_basic,  text=t("tab_basic"))
        nb.add(t_hotkey, text=t("tab_hotkey"))
        nb.add(t_theme,  text=t("tab_theme"))
        nb.add(t_gen,    text=t("tab_general"))

        self._build_basic_tab(t_basic, config, P, win)
        self._build_hotkey_tab(t_hotkey, config, P, win)
        self._build_theme_tab(t_theme, config, P, win)
        self._build_general_tab(t_gen, config, P, win)

        win.attributes("-alpha", config.get("theme_alpha", 0.95))
        self._apply_win_theme(config.get("theme_bg",   "#000000"),
                              config.get("theme_text", "#e8e8e8"),
                              config.get("theme_card", "#1c1c1c"))

    def _add_save_btn(self, tab, win, P):
        tk.Button(tab, text=t("save"), font=("Segoe UI", 9, "bold"),
                  bg=ACCENT, fg="#111", relief="flat", cursor="hand2",
                  command=lambda: self._save(win), width=12, pady=5
                  ).pack(side="bottom", anchor="e", padx=P, pady=(0, 14))
        tk.Frame(tab, bg=MUTED, height=1).pack(side="bottom", fill="x", padx=P, pady=(8, 0))

    def _build_basic_tab(self, tab, config, P, win):
        self._add_save_btn(tab, win, P)
        # ── API Key 1 ────────────────────────────────────────
        tk.Label(tab, text=t("api_key_1_label"), bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=P, pady=(14, 4))
        row1 = tk.Frame(tab, bg=BG)
        row1.pack(fill="x", padx=P)
        self._entry1 = tk.Entry(row1, show="•", font=("Segoe UI", 10),
                                bg=CARD, fg=TEXT, relief="flat",
                                insertbackground=ACCENT, bd=0)
        self._entry1.pack(side="left", expand=True, fill="x", ipady=7, padx=(0, 6))
        if config.get("api_key"):
            self._entry1.insert(0, config["api_key"])
        tk.Button(row1, text=t("show"), font=("Segoe UI", 8),
                  bg=CARD, fg=MUTED, relief="flat", cursor="hand2",
                  command=lambda: self._toggle_entry(self._entry1)
                  ).pack(side="left", ipady=7, padx=2)
        tk.Button(row1, text=t("get_key"), font=("Segoe UI", 8),
                  bg=CARD, fg=ACCENT, relief="flat", cursor="hand2",
                  command=lambda: webbrowser.open("https://aistudio.google.com")
                  ).pack(side="left", ipady=7, padx=2)

        # ── API Key 2 ────────────────────────────────────────
        tk.Label(tab, text=t("api_key_2_label"), bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=P, pady=(12, 4))
        row2 = tk.Frame(tab, bg=BG)
        row2.pack(fill="x", padx=P)
        self._entry2 = tk.Entry(row2, show="•", font=("Segoe UI", 10),
                                bg=CARD, fg=TEXT, relief="flat",
                                insertbackground=ACCENT, bd=0)
        self._entry2.pack(side="left", expand=True, fill="x", ipady=7, padx=(0, 6))
        if config.get("api_key_2"):
            self._entry2.insert(0, config["api_key_2"])
        tk.Button(row2, text=t("show"), font=("Segoe UI", 8),
                  bg=CARD, fg=MUTED, relief="flat", cursor="hand2",
                  command=lambda: self._toggle_entry(self._entry2)
                  ).pack(side="left", ipady=7, padx=2)
        q_btn = tk.Button(row2, text="?", font=("Segoe UI", 8, "bold"),
                          bg=CARD, fg=MUTED, relief="flat", cursor="hand2")
        q_btn.pack(side="left", ipady=7, padx=2)
        self._bind_tooltip(q_btn, t("tooltip_key2"))

        self.entry = self._entry1

        sep(tab)

        # ── 모델 선택 ─────────────────────────────────────────
        tk.Label(tab, text=t("gemini_model_label"), bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=P, pady=(0, 4))
        rec = t("recommended")
        self._models_display = [f"{m} ({rec})" if m == MODEL else m for m in MODELS]
        self._model_map      = dict(zip(self._models_display, MODELS))
        self._model_map_rev  = dict(zip(MODELS, self._models_display))
        saved = config.get("model", MODEL)
        self._model_var = tk.StringVar(value=self._model_map_rev.get(saved, saved))
        ttk.Combobox(tab, textvariable=self._model_var, values=self._models_display,
                     state="readonly", style="Dark.TCombobox",
                     font=("Segoe UI", 9)).pack(fill="x", padx=P, ipady=4)

        sep(tab)

        # ── 언어 선택 ─────────────────────────────────────────
        tk.Label(tab, text=t("language_label"), bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=P, pady=(0, 4))
        cur_display = LANG_CODES.get(config.get("language", "ko"), "한국어")
        self._lang_var = tk.StringVar(value=cur_display)
        ttk.Combobox(tab, textvariable=self._lang_var,
                     values=list(LANG_OPTIONS.keys()),
                     state="readonly", style="Dark.TCombobox",
                     font=("Segoe UI", 9)).pack(fill="x", padx=P, ipady=4)

    def _build_hotkey_tab(self, tab, config, P, win):
        self._add_save_btn(tab, win, P)
        tk.Label(tab, text=t("hotkey_hint"),
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=P, pady=(18, 14))

        for label_key, cfg_key in [("hotkey_screen_label", "hotkey"),
                                    ("hotkey_en_label",    "hotkey_en")]:
            row = tk.Frame(tab, bg=BG)
            row.pack(fill="x", padx=P, pady=(0, 10))
            tk.Label(row, text=f"{t(label_key)}:", bg=BG, fg=TEXT,
                     font=("Segoe UI", 9), width=12, anchor="w").pack(side="left")
            inner = tk.Frame(row, bg=BG)
            inner.pack(side="left", fill="x", expand=True)
            entry = HotkeyEntry(inner, config.get(cfg_key, HOTKEY if cfg_key == "hotkey" else HOTKEY_EN))
            if cfg_key == "hotkey": self._hk_entry    = entry
            else:                   self._hk_en_entry = entry

    def _build_theme_tab(self, tab, config, P, win):
        self._add_save_btn(tab, win, P)
        self._bg_color     = config.get("theme_bg", "#000000")
        self._current_bg   = BG
        self._current_text = TEXT
        self._current_card = CARD

        tk.Label(tab, text=t("theme_bg_label"), bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=P, pady=(18, 8))

        color_row = tk.Frame(tab, bg=BG)
        color_row.pack(anchor="w", padx=P)
        self._swatch_container = color_row
        self._color_borders    = {}

        for color in THEME_PRESETS:
            border = tk.Frame(color_row,
                              bg="white" if color == self._bg_color else MUTED,
                              padx=2, pady=2)
            border.pack(side="left", padx=(0, 10))
            swatch = tk.Frame(border, bg=color, width=44, height=44, cursor="hand2")
            swatch.pack()
            swatch.bind("<Button-1>", lambda e, c=color: self._select_color(c))
            border.bind("<Button-1>", lambda e, c=color: self._select_color(c))
            self._color_borders[color] = border

        sep(tab)

        tk.Label(tab, text=t("theme_alpha_label"), bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=P, pady=(0, 6))

        alpha_row = tk.Frame(tab, bg=BG)
        alpha_row.pack(anchor="w", padx=P)
        self._alpha_var = tk.DoubleVar(value=config.get("theme_alpha", 0.95))
        tk.Scale(alpha_row, from_=0.3, to=1.0, resolution=0.05, orient="horizontal",
                 variable=self._alpha_var, length=240,
                 bg=BG, fg=TEXT, troughcolor=CARD, highlightthickness=0,
                 activebackground=ACCENT, sliderrelief="flat", font=("Segoe UI", 7),
                 command=lambda v: win.attributes("-alpha", float(v))).pack(side="left")
        tk.Label(alpha_row, textvariable=self._alpha_var,
                 bg=BG, fg=MUTED, font=("Segoe UI", 8), width=4).pack(side="left", padx=(6, 0))

    def _build_general_tab(self, tab, config, P, win):
        self._add_save_btn(tab, win, P)
        tk.Label(tab, text=t("result_close_label"), bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=P, pady=(18, 8))

        self._close_var = tk.IntVar(value=1 if config.get("close_on_focusout", True) else 0)
        for lbl_key, val in [("close_on_focusout", 1), ("close_on_btn", 0)]:
            tk.Radiobutton(tab, text=t(lbl_key), variable=self._close_var, value=val,
                           bg=BG, fg=TEXT, selectcolor=CARD, activebackground=BG,
                           activeforeground=ACCENT, font=("Segoe UI", 9),
                           cursor="hand2").pack(anchor="w", padx=P + 4, pady=2)

        sep(tab)

        self._auto_var = tk.BooleanVar(value=config.get("autostart", False))
        tk.Checkbutton(tab, text=t("autostart_label"),
                       variable=self._auto_var, bg=BG, fg=TEXT, selectcolor=CARD,
                       activebackground=BG, activeforeground=ACCENT,
                       font=("Segoe UI", 9), cursor="hand2").pack(anchor="w", padx=P)

    # ── 내부 메서드 ───────────────────────────────────────────

    def _select_color(self, color):
        self._bg_color = color
        for c, border in self._color_borders.items():
            border.config(bg="white" if c == color else MUTED)
        self._apply_win_theme(color, theme_text(color), theme_card(color))

    def _apply_win_theme(self, bg, text, card):
        def walk(widget):
            if widget is self._swatch_container:
                return
            try:
                if widget.cget("bg") in (self._current_bg, BG):
                    widget.configure(bg=bg)
                elif widget.cget("bg") in (self._current_card, CARD):
                    widget.configure(bg=card)
            except Exception:
                pass
            try:
                if widget.cget("fg") in (self._current_text, TEXT):
                    widget.configure(fg=text)
            except Exception:
                pass
            try:
                if widget.cget("readonlybackground") in (self._current_card, CARD):
                    widget.configure(readonlybackground=card)
            except Exception:
                pass
            for child in widget.winfo_children():
                walk(child)

        walk(self._win)
        self._style.configure("Dark.TNotebook", background=bg)
        self._style.configure("Dark.TNotebook.Tab", background=card, foreground=text)
        self._style.map("Dark.TNotebook.Tab",
                        background=[("selected", bg)],
                        foreground=[("selected", ACCENT)])
        self._style.configure("Dark.TCombobox",
                              fieldbackground=card, background=card,
                              foreground=text, selectbackground=card,
                              lightcolor=card, darkcolor=card)
        self._style.map("Dark.TCombobox",
                        fieldbackground=[("readonly", card)],
                        foreground=[("readonly", text)])
        self._current_bg   = bg
        self._current_text = text
        self._current_card = card

    def _bind_tooltip(self, widget, text):
        tip = [None]

        def show(e):
            tip[0] = tk.Toplevel(widget)
            tip[0].overrideredirect(True)
            tip[0].attributes("-topmost", True)
            tk.Label(tip[0], text=text, bg="#2a2a2a", fg=TEXT,
                     font=("Segoe UI", 8), padx=8, pady=6,
                     justify="left").pack()
            tip[0].update_idletasks()
            tip[0].geometry(f"+{e.x_root + 12}+{e.y_root + 20}")

        def hide(e):
            if tip[0]:
                tip[0].destroy()
                tip[0] = None

        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)

    def _toggle_entry(self, entry):
        entry.config(show="" if entry.cget("show") == "•" else "•")

    def _save(self, win):
        key = self._entry1.get().strip()
        if not key:
            messagebox.showwarning(t("warn_title"), t("warn_no_api_key"), parent=win)
            return
        lang = LANG_OPTIONS.get(self._lang_var.get(), "ko")
        i18n_load(lang)

        autostart = self._auto_var.get()
        self.config["api_key"]           = key
        self.config["api_key_2"]         = self._entry2.get().strip()
        self.config["language"]          = lang
        self.config["close_on_focusout"] = bool(self._close_var.get())
        self.config["autostart"]         = autostart
        self.config["model"]             = self._model_map.get(self._model_var.get(), self._model_var.get())
        self.config["hotkey"]            = self._hk_entry.get()
        self.config["hotkey_en"]         = self._hk_en_entry.get()
        self.config["theme_bg"]          = self._bg_color
        self.config["theme_text"]        = theme_text(self._bg_color)
        self.config["theme_card"]        = theme_card(self._bg_color)
        self.config["theme_alpha"]       = round(self._alpha_var.get(), 2)
        save_config(self.config)
        set_autostart(autostart)
        self.on_save(key)
        win.destroy()
