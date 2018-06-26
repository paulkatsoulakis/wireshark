# windeployqt-to-nsh
#
# Windeployqt-to-nsh - Convert the output of windeployqt to an equivalent set of
# NSIS "File" function calls.
#
# Copyright 2014 Gerald Combs <gerald@wireshark.org>
#
# Wireshark - Network traffic analyzer
# By Gerald Combs <gerald@wireshark.org>
# Copyright 1998 Gerald Combs
#
# SPDX-License-Identifier: GPL-2.0-or-later

#requires -version 2

<#
.SYNOPSIS
Creates NSIS "File" function calls required for Qt packaging.

.DESCRIPTION
This script creates an NSIS-compatible file based on the following Qt
versions:

  - 5.3 and later: A list of DLLs and directories based on the output of the
    "windeployqt" utility. Windeployqt lists the DLLs required to run a Qt
    application. (The initial version that shipped with Qt 5.2 is unusable.)

  - 5.2 and earlier: A hard-coded list of Qt DLLs and directories appropriate
    for earlier Qt versions.

  - None: A dummy file.

If building with Qt, QMake must be in your PATH.

.PARAMETER Executable
The path to a Qt application. It will be examined for dependent DLLs.

.PARAMETER FilePath
Output filename.

.INPUTS
-Executable Path to the Qt application.
-FilePath Output NSIS file.

.OUTPUTS
List of NSIS commands required to package supporting DLLs.

.EXAMPLE
C:\PS> .\windeployqt-to-nsis.ps1 windeployqt.exe ..\..\staging\wireshark.exe qt-dll-manifest.nsh
#>

Param(
    [Parameter(Mandatory=$true, Position=0)]
    [String] $Executable,

    [Parameter(Position=1)]
    [String] $FilePath = "qt-dll-manifest.nsh"
)


try {
    $qtVersion = [version](qmake -query QT_VERSION)
    $nsisCommands = @("# Qt version " + $qtVersion ; "#")

    if ($qtVersion -ge "5.3") {
        # Qt 5.3 or later. Windeployqt is present and works

        $wdqtList = windeployqt `
            --release `
            --no-compiler-runtime `
            --list relative `
            $Executable

        $dllPath = Split-Path -Parent $Executable

        $dllList = @()
        $dirList = @()

        foreach ($entry in $wdqtList) {
            $dir = Split-Path -Parent $entry
            if ($dir) {
                $dirList += "File /r `"$dllPath\$dir`""
            } else {
                $dllList += "File `"$dllPath\$entry`""
            }
        }

        $dirList = $dirList | Sort-Object | Get-Unique

        $nsisCommands += $dllList + $dirList

    } elseif ($qtVersion -ge "5.0") {
        # Qt 5.0 - 5.2. Windeployqt is buggy or not present

        $nsisCommands += @"
File "..\..\wireshark-qt-release\Qt5Core.dll"
File "..\..\wireshark-qt-release\Qt5Gui.dll"
File "..\..\wireshark-qt-release\Qt5Widgets.dll"
File "..\..\wireshark-qt-release\Qt5PrintSupport.dll"
File /r "..\..\wireshark-qt-release\platforms"
"@

    }
}

catch {

    $nsisCommands = @"
# Qt not configured
#
"@

}

Set-Content $FilePath @"
#
# Automatically generated by $($MyInvocation.MyCommand.Name)
#
"@

Add-Content $FilePath $nsisCommands
