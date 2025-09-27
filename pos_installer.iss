#define MyAppName "Chambu_POS"
#define MyAppVersion "1.0"
#define MyAppPublisher "Chambu digital"
#define MyAppURL "http://www.chambudigital.co.ke/"
#define MyAppExeName "Chambu_SmartPOS.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-47H8-I9J0-K1L2M3N4O5P6}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
PrivilegesRequired=admin
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\Chambu_POS
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=Chambu_SmartPOS_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=pos_icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Start when Windows starts"; GroupDescription: "Windows Startup:"
Name: "pintotaskbar"; Description: "Pin to taskbar"; GroupDescription: "Additional options:"; Flags: checkedonce

[Files]
; Include the main executable from the dist folder
Source: "dist\Chambu_SmartPOS.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Add the program to Windows Startup if selected
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Add to Windows startup if selected
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletevalue; Tasks: startupicon

[Code]
// Function to pin application to taskbar
procedure PinToTaskbar();
var
  Shell: Variant;
  AppPath: string;
begin
  try
    Shell := CreateOleObject('Shell.Application');
    AppPath := ExpandConstant('{app}\{#MyAppExeName}');
    Shell.Namespace(ExtractFileDir(AppPath)).ParseName(ExtractFileName(AppPath)).Verbs.Item(5386).DoIt;
  except
    // Fail silently if pinning is not supported
  end;
end;

// Called during setup to perform additional tasks
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if IsTaskSelected('pintotaskbar') then
    begin
      PinToTaskbar();
    end;
  end;
end;
