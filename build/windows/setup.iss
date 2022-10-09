#define Name "Discord.fm"
#define Version "#VERSION#"
#define Publisher "androidWG"
#define InfoURL "https://github.com/androidWG/Discord.fm"
#define UpdatesURL "https://github.com/androidWG/Discord.fm/releases/latest"
#define LocalPath "#REPO#"
#define Suffix "#SUFFIX#"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{5DD6EAF6-9E8F-4240-ADF1-29FD79B30E3F}
AppName={#Name}
AppVersion={#Version}
AppVerName={#Name} v{#Version}
AppPublisher={#Publisher}
AppPublisherURL={#InfoURL}
AppSupportURL={#InfoURL}
AppUpdatesURL={#UpdatesURL}
DefaultDirName={localappdata}\Programs\{#Name}
DisableProgramGroupPage=yes
CloseApplications=force
AllowNoIcons=no
OutputDir={#LocalPath}\dist
OutputBaseFilename=discord.fm-setup-win64-#VERSION##SUFFIX#
SetupIconFile={#LocalPath}\src\resources\settings.ico
SolidCompression=yes
UninstallDisplayName={#Name}
UninstallDisplayIcon={app}\discord_fm.exe
MinVersion=0,6.1
WizardStyle=modern
WizardSizePercent=100
RestartIfNeededByRun=False
VersionInfoVersion={#Version}
VersionInfoDescription=Show your Last.fm status on Discord
VersionInfoProductName={#Name}
VersionInfoProductVersion={#Version}
ShowLanguageDialog=auto
RestartApplications=True
DisableWelcomePage=False
UsePreviousSetupType=False
UsePreviousLanguage=False
AlwaysShowGroupOnReadyPage=True
AlwaysUsePersonalGroup=True
AppendDefaultGroupName=False
DefaultGroupName={#Name}
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
VersionInfoCompany=androidWG/Sam Rodrigues
VersionInfoProductTextVersion={#Version}
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64
DisableReadyMemo=True

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#LocalPath}\dist\discord_fm\*"; DestDir: "{app}"; Flags: ignoreversion createallsubdirs recursesubdirs

[Registry]
Root: "HKCU"; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueName: "{#Name}"; Flags: deletevalue

[Run]
Filename: "{app}\discord_fm.exe"; Description: "Launch Discord.fm"; Flags: postinstall nowait

[ThirdParty]
CompileLogFile={#LocalPath}\dist\#VERSION##SUFFIX#-installer.log

[Icons]
Name: "{userstartmenu}\Discord.fm Settings"; Filename: "{app}\settings_ui.exe"; IconFilename: "{app}\settings_ui.exe"
Name: "{userstartup}\{#Name}"; Filename: "{app}\discord_fm.exe"; Tasks: StartWithWindows

[InstallDelete]
Type: filesandordirs; Name: "{app}"

[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/T /IM discord_fm.exe /F"; Flags: waituntilterminated runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{localappdata}\{#Name}"
Type: filesandordirs; Name: "{userappdata}\{#Name}"
Type: files; Name: "{userstartup}\{#Name}.lnk"

[Tasks]
Name: "StartWithWindows"; Description: "Start Discord.fm with Windows"
