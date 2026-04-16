Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
cmd = "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & root & "\start_app_background.ps1"""
shell.Run cmd, 0, False

