import tkinter as tk
from tkinter import messagebox
import threading
import keyboard
import pystray
from PIL import ImageGrab, ImageEnhance, ImageFilter, Image
import google.generativeai as genai

from core.config import (
    APP_NAME, HOTKEY, HOTKEY_EN, MODEL,
    load_config, _find_asset, make_prompt,
)
from core.theme import BG, CARD, ACCENT, TEXT, MUTED
from core.i18n import t, load as i18n_load, LANG_NAMES
from ui.settings_win import SettingsWindow
from ui.input_win   import InputWindow
from ui.overlay     import DragOverlay
from ui.loading     import LoadingIndicator
from ui.result_win  import ResultWindow


class App:
    def __init__(self):
        self.config    = load_config()
        i18n_load(self.config.get("language", "ko"))

        self._models   = [None, None]
        self._model_idx = 0
        self._req_id   = 0
        self._loader   = None

        self.root = tk.Tk()
        self.root.withdraw()

        if not self.config.get("api_key"):
            self.root.after(100, lambda: SettingsWindow(
                self.root, self.config, self._on_settings_saved, first_run=True))
        else:
            self._init_models()

        self._register_hotkeys()
        self._setup_tray()

        self.root.after(500, self._startup_toast)
        self.root.mainloop()

    # ── 초기화 ────────────────────────────────────────────────

    def _make_model(self, key):
        genai.configure(api_key=key)
        return genai.GenerativeModel(
            self.config.get("model", MODEL),
            generation_config=genai.GenerationConfig(temperature=0)
        )

    def _init_models(self):
        self._models   = [None, None]
        self._model_idx = 0
        key1 = self.config.get("api_key",   "")
        key2 = self.config.get("api_key_2", "")
        try:
            if key1:
                self._models[0] = self._make_model(key1)
            if key2:
                self._models[1] = self._make_model(key2)
        except Exception as e:
            messagebox.showerror(t("err_title"), t("err_gemini_init", e=e))

    @property
    def model(self):
        return self._models[self._model_idx]

    def _is_rate_limit(self, e):
        msg = str(e).lower()
        return any(k in msg for k in ("429", "quota", "resource exhausted", "rate limit"))

    def _setup_tray(self):
        icon_path = _find_asset("puyo_trans.ico")
        img = Image.open(icon_path) if icon_path else Image.new("RGB", (64, 64), "#1a1a1a")
        if icon_path:
            self.root.after(0, lambda: self.root.iconbitmap(icon_path))
        menu = pystray.Menu(
            pystray.MenuItem(APP_NAME, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("설정", lambda: self.root.after(0, self._show_settings)),
            pystray.MenuItem("종료", self._quit)
        )
        self.tray = pystray.Icon("NexusTK", img, APP_NAME, menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

    def _register_hotkeys(self):
        keyboard.unhook_all()
        hk    = self.config.get("hotkey",    HOTKEY)
        hk_en = self.config.get("hotkey_en", HOTKEY_EN)
        try:
            keyboard.add_hotkey(hk,    lambda: self.root.after(0, self._show_overlay))
            keyboard.add_hotkey(hk_en, lambda: self.root.after(0, self._show_input))
        except Exception as e:
            messagebox.showerror(t("err_title"), t("err_hotkey", e=e))

    # ── UI 이벤트 ─────────────────────────────────────────────

    def _on_settings_saved(self, key):
        self._init_models()
        self._register_hotkeys()

    def _show_settings(self):
        keyboard.unhook_all()
        SettingsWindow(self.root, self.config, self._on_settings_saved,
                       on_close=self._register_hotkeys)

    def _show_input(self):
        if not self.model:
            messagebox.showwarning(t("warn_title"), t("warn_no_api"))
            return
        theme = {
            "bg":     self.config.get("theme_bg",    BG),
            "card":   self.config.get("theme_card",  CARD),
            "text":   self.config.get("theme_text",  TEXT),
            "alpha":  self.config.get("theme_alpha", 0.96),
            "accent": ACCENT,
            "muted":  MUTED,
        }
        cfg_lang = self.config.get("language", "en")
        default_target = "id" if cfg_lang == "en" else "en"

        def translate_text(text, target_lang_code):
            target_name = LANG_NAMES.get(target_lang_code, "English")
            prompt = (
                f"Detect the language of the following text and translate it into {target_name}. "
                f"Reply with only the translation:\n{text}"
            )
            return self._translate_with_fallback(prompt)

        InputWindow(self.root, translate_text, theme, default_target=default_target)

    def _show_overlay(self):
        if not self.model:
            messagebox.showwarning(t("warn_title"), t("warn_no_api"))
            self._show_settings()
            return
        if self._loader:
            self._loader.close()
            self._loader = None
        self._req_id += 1
        DragOverlay(self.root, self._on_region)

    def _quit(self, *args):
        keyboard.unhook_all()
        self.tray.stop()
        self.root.after(0, self.root.destroy)

    # ── 번역 파이프라인 ───────────────────────────────────────

    def _on_region(self, x1, y1, x2, y2):
        my_id = self._req_id
        try:
            self._loader = LoadingIndicator(
                self.root, x1, x2, y2,
                card_color=self.config.get("theme_card", CARD),
                alpha=self.config.get("theme_alpha", 0.88),
                text_color=self.config.get("theme_text", TEXT),
            )
        except Exception as e:
            print(t("err_loader", e=e))
            return
        threading.Thread(
            target=self._process,
            args=(x1, y1, x2, y2, my_id, self._loader),
            daemon=True,
        ).start()

    def _process(self, x1, y1, x2, y2, my_id, loader):
        try:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            w, h = img.size
            img = img.resize((w * 2, h * 2), resample=0)
            img = img.filter(ImageFilter.SHARPEN)
            img = ImageEnhance.Contrast(img).enhance(1.5)

            target_lang = LANG_NAMES.get(self.config.get("language", "en"), "English")
            result = self._translate_with_fallback([make_prompt(target_lang), img])

            if my_id != self._req_id:
                self.root.after(0, loader.close)
                return

            self._show_result(result, x1, x2, y2, loader)
        except Exception as e:
            import traceback; traceback.print_exc()
            err = t("translate_error", etype=type(e).__name__, e=e)
            self._show_result(err, x1, x2, y2, loader, error=True)

    def _translate_with_fallback(self, payload):
        other_idx = 1 - self._model_idx
        try:
            response = self.model.generate_content(payload)
            return response.text.strip() if response.text else t("ocr_fail")
        except Exception as e:
            if self._is_rate_limit(e) and self._models[other_idx]:
                self._model_idx = other_idx
                response = self.model.generate_content(payload)
                return response.text.strip() if response.text else t("ocr_fail")
            raise

    def _show_result(self, text, x1, x2, y2, loader, error=False):
        close_fo   = self.config.get("close_on_focusout", True)
        bg_color   = self.config.get("theme_bg",   BG)
        text_color = "#ff6b6b" if error else self.config.get("theme_text", TEXT)
        card_color = self.config.get("theme_card", CARD)
        alpha      = self.config.get("theme_alpha", 0.95)
        self.root.after(0, loader.close)
        self.root.after(0, lambda: ResultWindow(
            self.root, text, x1, x2, y2,
            close_fo, bg_color, alpha, text_color, card_color))

    # ── 시작 토스트 ───────────────────────────────────────────

    def _startup_toast(self):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = 300, 64
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.0)
        win.configure(bg=CARD)
        win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        hk    = self.config.get("hotkey",    HOTKEY).upper()
        hk_en = self.config.get("hotkey_en", HOTKEY_EN).upper()
        tk.Label(win, text=APP_NAME, bg=CARD, fg=ACCENT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(10, 2))
        tk.Label(win, text=t("toast_hint", hk=hk, hk_en=hk_en),
                 bg=CARD, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=14)

        def fade(alpha, step, delay, done=None):
            alpha = round(alpha + step, 2)
            alpha = max(0.0, min(1.0, alpha))
            win.attributes("-alpha", alpha)
            if (step > 0 and alpha < 0.92) or (step < 0 and alpha > 0.0):
                win.after(delay, lambda: fade(alpha, step, delay, done))
            elif done:
                done()

        fade(0.0, 0.08, 30)
        win.after(2500, lambda: fade(0.92, -0.06, 40, done=win.destroy))


if __name__ == "__main__":
    App()
