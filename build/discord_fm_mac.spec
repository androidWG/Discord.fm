# -*- mode: python ; coding: utf-8 -*-
from globals import __version

block_cipher = None


a = Analysis(['main.py'],
             pathex=['/Users/samuel/Repos/Discord.fm'],
             binaries=[],
             datas=[('resources/black/.', 'resources/black'), ('resources/white/.', 'resources/white'), ('.env', '.')],
             hiddenimports=[],
             hookspath=['hooks'],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='discord_fm',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='resources/icon.icns')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='discord_fm')

app = BUNDLE(coll,
             name='Discord.fm.app',
             icon='resources/icon.icns',
             info_plist={
                'CFBundleVersion': __version,
                'LSUIElement': True,
                'LSBackgroundOnly': True
             },
             bundle_identifier='com.androidwg.discordfm')
