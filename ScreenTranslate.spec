# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('puyo_trans.ico', '.'), ('locales', 'locales')]
binaries = []
hiddenimports = ['winocr', 'winrt.windows.media.ocr', 'winrt.windows.graphics.imaging', 'winrt.windows.storage.streams', 'pystray',
                 'core', 'core.config', 'core.theme', 'core.i18n',
                 'ui', 'ui.widgets', 'ui.settings_win', 'ui.input_win',
                 'ui.overlay', 'ui.loading', 'ui.result_win']
tmp_ret = collect_all('pystray')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['screen_translate.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ScreenTranslate',
    icon='puyo_trans.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
