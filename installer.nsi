; SinhalaWord Installer Script
; Created for NSIS 3.0 or higher

!include "MUI2.nsh"
!include "FileFunc.nsh"

; Define application name and version
!define APPNAME "SinhalaWord"
!define APPVERSION "1.0.0"
!define PUBLISHER "SinhalaWord"
!define WEBSITE "https://sinhalaword.com"

; Define installation directory and registry keys
!define INSTALLDIR "$PROGRAMFILES\${APPNAME}"
!define REGKEY "Software\${APPNAME}"

; General settings
Name "${APPNAME} ${APPVERSION}"
OutFile "dist\${APPNAME}_Setup.exe"
InstallDir "${INSTALLDIR}"
InstallDirRegKey HKLM "${REGKEY}" "InstallDir"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "resources\splash\sinhalaword_icon.ico"
!define MUI_UNICON "resources\splash\sinhalaword_icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "resources\splash\sinhalaword.png"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "resources\splash\sinhalaword.png"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installation section
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Add files to install
    File "dist\SinhalaWord.exe"
    File /r "dist\SinhalaWord_Portable\*.*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\SinhalaWord.exe"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\SinhalaWord.exe"
    
    ; Write registry keys
    WriteRegStr HKLM "${REGKEY}" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "${REGKEY}\Components" "Main" 1
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Add uninstall information to Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\SinhalaWord.exe,0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${APPVERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${WEBSITE}"
    
    ; Get installation size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" "$0"
SectionEnd

; Uninstallation section
Section "Uninstall"
    ; Remove files and directories
    Delete "$INSTDIR\SinhalaWord.exe"
    Delete "$INSTDIR\uninstall.exe"
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    Delete "$DESKTOP\${APPNAME}.lnk"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKLM "${REGKEY}"
SectionEnd