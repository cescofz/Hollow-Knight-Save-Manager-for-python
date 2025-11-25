# pack.spec
import sys
import os
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
root_path = os.path.abspath(".")

a = Analysis(
    ["main.py"], 
    pathex=[root_path],
    binaries=[],
    datas=[
        (os.path.join(root_path, "res"), "res"), 
        (os.path.join(root_path, "UI.py"), ".")
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="HollowKnight存档修改器", 
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    runtime_tmpdir=None,
    console=False, 
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="E:\\icon.ico",
)