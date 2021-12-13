# -*- mode: python ; coding: utf-8 -*-
from main import __version

block_cipher = None


a = Analysis(['ui/ui.py'],
             pathex=['/Users/samuel/Repos/Discord.fm'],
             binaries=[],
             datas=[('resources/black/.', 'resources/black'), ('resources/white/.', 'resources/white')],
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
          name='settings_ui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='resources/settings.icns')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               upx_exclude=[],
               name='settings_ui')

app = BUNDLE(coll,
             name='Discord.fm Settings.app',
             icon='resources/settings.icns',
             info_plist={
                'CFBundleVersion': __version,
                'NSRequiresAquaSystemAppearance': False
             },
             bundle_identifier='com.androidwg.discordfm.ui')
