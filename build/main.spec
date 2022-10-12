# -*- mode: python ; coding: utf-8 -*-

main_a = Analysis(
    ["src/main.py"],
    hiddenimports=["plyer.platforms.win.notification"],
    datas=[
        ("src/resources/black/.", "resources/black"),
        ("src/resources/white/.", "resources/white"),
        ("src/resources/settings.png", "resources"),
    ],
    hookspath=["hooks"],
)

main_pyz = PYZ(main_a.pure, main_a.zipped_data)

main_exe = EXE(
    main_pyz,
    main_a.scripts,
    exclude_binaries=True,
    name="discord_fm",
    console=False,
    version=r"#VER_MAIN#",
    icon=r"#ICON_MAIN#",
)

coll = COLLECT(
    main_exe,
    main_a.binaries,
    main_a.zipfiles,
    main_a.datas,
    upx=True,
    name="discord_fm",
)
