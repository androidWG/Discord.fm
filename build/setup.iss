#define Name "Discord.fm"
#define Version "#VERSION#"
#define Publisher "androidWG"
#define InfoURL "https://github.com/AndroidWG/Discord.fm"
#define LocalPath "#REPO#"
#define Suffix "#SUFFIX#"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{5DD6EAF6-9E8F-4240-ADF1-29FD79B30E3F}
AppName={#Name}
AppVersion={#Version}
;AppVerName={#Name} {#Version}
AppPublisher={#Publisher}
AppPublisherURL={#InfoURL}
AppSupportURL={#InfoURL}
AppUpdatesURL={#InfoURL}
DefaultDirName={localappdata}\Programs\{#Name}
DisableProgramGroupPage=yes
CloseApplications=force
AllowNoIcons=no
OutputDir={#LocalPath}\dist
OutputBaseFilename=discord.fm-setup-win64-{#Version}{#Suffix}
SetupIconFile={#LocalPath}\resources\icon.ico
SolidCompression=yes
UninstallDisplayName=Discord.fm
UninstallDisplayIcon={app}\discord_fm.exe
MinVersion=0,6.1
WizardStyle=modern
WizardSizePercent=100
RestartIfNeededByRun=False
VersionInfoVersion={#Version}
VersionInfoDescription=Show your Last.fm status on Discord
VersionInfoProductName=Discord.fm
VersionInfoProductVersion={#Version}
ShowLanguageDialog=auto
RestartApplications=True
DisableWelcomePage=False
UsePreviousSetupType=False
UsePreviousLanguage=False
AlwaysShowGroupOnReadyPage=True
AlwaysUsePersonalGroup=True
AppendDefaultGroupName=False
UsePreviousGroup=False
DefaultGroupName=Discord.fm
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
VersionInfoCompany=androidWG/Samuel Rodrigues
VersionInfoProductTextVersion={#Version}
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64
DisableReadyMemo=True

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#LocalPath}\dist\discord_fm.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#LocalPath}\dist\settings_ui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#Name}"; ValueData: "{app}\discord_fm.exe";
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueName: "{#Name}"; Flags: uninsdeletevalue;

[Run]
Filename: "{app}\discord_fm.exe"; Description: "Launch Discord.fm"; Flags: postinstall nowait

[ThirdParty]
CompileLogFile={#LocalPath}\dist\{#Version}{#Suffix}-installer.log

[Icons]
Name: "{userstartmenu}\Discord.fm Settings"; Filename: "{app}\settings_ui.exe"; IconFilename: "{app}\discord_fm.exe"

[InstallDelete]
Type: filesandordirs; Name: "{app}"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{localappdata}\Discord.fm"
Type: filesandordirs; Name: "{appdata}\Discord.fm"
