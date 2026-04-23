import os
import sys
import json
import winreg
from tkinter import messagebox
from core.i18n import t

APP_NAME  = "NexusTK DragTranslater"
REG_KEY   = "NexusTK번역기"
HOTKEY    = "alt+q"
HOTKEY_EN = "alt+e"
MODEL     = "gemini-3.1-flash-lite-preview"
MODELS    = [
    "gemini-3.1-flash-lite-preview",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]
MODELS_DISPLAY = [f"{m} (권장)" if m == MODEL else m for m in MODELS]

def make_prompt(target_lang: str) -> str:
    return (
        "This is a screenshot from a game. "
        f"Automatically detect the language of the visible text, then translate it into {target_lang}. "
        "Every sentence and phrase MUST be translated — do not leave any text in its original language. "
        f"Only keep individual proper nouns, item names, and skill names untranslated when naturally embedded inside a {target_lang} sentence. "
        "Do not add, infer, or imagine any content not explicitly shown. "
        "Reply with only the translation. No explanations, no extra text."
    )


def _base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # 개발 환경: core/config.py → ScreenTranslate/
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_asset(filename):
    path = os.path.join(_base_dir(), filename)
    if os.path.exists(path):
        return path
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        path = os.path.join(meipass, filename)
        if os.path.exists(path):
            return path
    return None


CONFIG_PATH = os.path.join(_base_dir(), "config.json")


def load_config():
    defaults = {
        "api_key":  "",
        "api_key_2": "",
        "language": "en",
        "close_on_focusout": True,
        "autostart": False,
        "model": MODEL,
        "hotkey": HOTKEY,
        "hotkey_en": HOTKEY_EN,
        "theme_bg":   "#000000",
        "theme_text": "#e8e8e8",
        "theme_card": "#1c1c1c",
        "theme_alpha": 0.95,
        "font_size": 10,
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                defaults.update(json.load(f))
        except Exception:
            pass
    return defaults


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_exe_path():
    return sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)


def set_autostart(enabled):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        if enabled:
            winreg.SetValueEx(key, REG_KEY, 0, winreg.REG_SZ, f'"{get_exe_path()}"')
        else:
            try:
                winreg.DeleteValue(key, REG_KEY)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        messagebox.showerror(t("err_title"), t("err_autostart", e=e))
