[Setup]
AppId={{DDAAB0A7-CF81-4CF5-86DE-4B6F0C53C641}
AppName=Aura-Clicker
AppVersion=0.1.6
AppPublisher=Aura Néo
AppPublisherURL=https://auraneo.fr
DefaultDirName={autopf}\Aura-Clicker
DefaultGroupName=Aura-Clicker
DisableProgramGroupPage=yes
OutputDir=..\dist-installer
OutputBaseFilename=Aura-Clicker-Setup-0.1.6
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=..\aura_clicker\assets\logo_aura_clicker.ico
UninstallDisplayIcon={app}\Aura-Clicker.exe

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer une icône sur le Bureau"; GroupDescription: "Icônes supplémentaires:"; Flags: unchecked

[Files]
Source: "..\dist\Aura-Clicker\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Aura-Clicker"; Filename: "{app}\Aura-Clicker.exe"; IconFilename: "{app}\Aura-Clicker.exe"
Name: "{autodesktop}\Aura-Clicker"; Filename: "{app}\Aura-Clicker.exe"; IconFilename: "{app}\Aura-Clicker.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Aura-Clicker.exe"; Description: "Lancer Aura-Clicker"; Flags: nowait postinstall skipifsilent
