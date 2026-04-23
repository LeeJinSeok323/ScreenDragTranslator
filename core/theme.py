BG     = "#111111"
CARD   = "#1c1c1c"
ACCENT = "#c9a227"
TEXT   = "#e8e8e8"
MUTED  = "#555555"

THEME_PRESETS = [
    "#000000",
    "#f0f0f0",
    "#1a1a2e",
    "#7dbde1",
]
THEME_TEXT_MAP = {
    "#000000": "#e8e8e8",
    "#f0f0f0": "#111111",
    "#1a1a2e": "#e8e8e8",
    "#7dbde1": "#111111",
}
THEME_CARD_MAP = {
    "#000000": "#1c1c1c",
    "#f0f0f0": "#d8d8d8",
    "#1a1a2e": "#16213e",
    "#7dbde1": "#5aa8d4",
}


def theme_text(bg):
    return THEME_TEXT_MAP.get(bg.lower(), "#e8e8e8")


def theme_card(bg):
    return THEME_CARD_MAP.get(bg.lower(), "#1c1c1c")
