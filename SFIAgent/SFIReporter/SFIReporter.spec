# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\sfi_reporter\\app.py'],
    pathex=['..\\accia-s360\\src'],
    binaries=[],
    datas=[],
    hiddenimports=['sfi_reporter.models', 'sfi_reporter.formatters', 'sfi_reporter.services', 'sfi_reporter.dialogs', 'sfi_reporter.app', 'sfi_reporter.copilot_panel', 'sfi_reporter.query_builder', 'sfi_reporter.eta_logic', 'copilot', 'accia_s360', 'accia_s360.client', 'accia_s360.models', 'accia_s360.auth', 'accia_s360.cache', 'accia_s360.config', 'accia_s360.exceptions'],
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
    name='SFIReporter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
