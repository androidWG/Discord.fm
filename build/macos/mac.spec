# -*- mode: python ; coding: utf-8 -*-

main_a = Analysis(['src/main.py'],
             datas=[('src/resources/black/.', 'resources/black'),
             ('src/resources/white/.', 'resources/white'),
             ('src/.env', '.')],
             hiddenimports=['wrappers.last_fm_user','aquaui.notification.native_notification'],
             hookspath=['hooks'],
             noarchive=False)
main_pyz = PYZ(main_a.pure, main_a.zipped_data)

main_exe = EXE(main_pyz,
    main_a.scripts,
    exclude_binaries=True,
    name='discord_fm',
    console=False,
    disable_windowed_traceback=False,
    icon='resources/icon.icns')

ui_a = Analysis(
    ['src/ui.py'],
    hiddenimports=['plyer.platforms.win.notification'],
    datas=[('src/resources/black/.', 'resources/black'),
        ('src/resources/white/.', 'resources/white'),
        ('src/resources/settings.png', 'resources'),
        ('src/.env', '.')],
    hookspath=['hooks'],
)
ui_pyz = PYZ(ui_a.pure, ui_a.zipped_data)

ui_exe = EXE(
    ui_pyz,
    ui_a.scripts,
    exclude_binaries=True,
    name='ui',
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    main_exe,
    main_a.binaries,
    main_a.zipfiles,
    main_a.datas,
    ui_exe,
    ui_a.binaries,
    ui_a.zipfiles,
    ui_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='discord_fm')

app = BUNDLE(coll,
    name='Discord.fm.app',
    icon='src/resources/icon.icns',
    info_plist={
        'CFBundleVersion': #VERSION#,
        'LSUIElement': True,
        'LSBackgroundOnly': True
    },
    bundle_identifier='com.androidwg.discordfm')
