# -*- mode: python ; coding: utf-8 -*-
# pyinstaller --clean --hidden-import="pystray._win32" --additional-hooks-dir="hooks" --onefile --name="Last.fm Discord Rich Presence" --icon="assets\icon.ico" --noconsole main_old.py

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\gusta\\Desktop\\Projetos\\Last.fm\\Last.fm-Discord-Rich-Presence'],
             binaries=[],
             datas=[],
             hiddenimports=['pystray._win32'],
             hookspath=['hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Last.fm Discord Rich Presence',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='assets\\icon.ico')
