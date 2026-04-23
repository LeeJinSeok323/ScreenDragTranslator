@echo off
pip install pyinstaller pillow keyboard pystray google-generativeai
python -m PyInstaller ScreenTranslate.spec --clean
pause
