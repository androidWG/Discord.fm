# -*- mode: python ; coding: utf-8 -*-

ui_a = Analysis(
    ['src/ui.py'],
    hiddenimports=['wrappers.last_fm_user'],
    hookspath=['hooks'],
)
main_a = Analysis(
    ['src/main.py'],
    hiddenimports=['plyer.platforms.win.notification'],
    datas=[
        ('src/resources/black/.', 'resources/black'),
        ('src/resources/white/.', 'resources/white'),
        ('src/resources/settings.png', 'resources'),
        ('src/.env', '.')],
    hookspath=['hooks'],
)

MERGE((main_a, 'discord_fm', 'discord_fm'), (ui_a, 'settings_ui', 'settings_ui'))

ui_pyz = PYZ(ui_a.pure, ui_a.zipped_data)
main_pyz = PYZ(main_a.pure, main_a.zipped_data)

ui_exe = EXE(
    ui_pyz,
    ui_a.scripts,
    exclude_binaries=True,
    name='settings_ui',
    upx=True,
    console=False,
    version=r'#VER_UI#',
    icon=r'#ICON_UI#',
)
main_exe = EXE(
    main_pyz,
    main_a.scripts,
    exclude_binaries=True,
    name='discord_fm',
    console=False,
    version=r'#VER_MAIN#',
    icon=r'#ICON_MAIN#',
)

coll = COLLECT(
    ui_exe,
    ui_a.binaries,
    ui_a.zipfiles,
    ui_a.datas,
    main_exe,
    main_a.binaries,
    main_a.zipfiles,
    main_a.datas,
    upx=True,
    name='discord_fm',
)