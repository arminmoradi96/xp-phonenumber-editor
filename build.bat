@echo off
setlocal
cd /d "%~dp0"
py -m PyInstaller --noconfirm --clean --onefile --windowed --name "XP-Phone-Editor" --version-file "version_info.txt" "phone_inf_editor_bilingual.py"
if errorlevel 1 (
  echo Build failed.
  exit /b 1
)
echo Done: dist\XP-Phone-Editor.exe
endlocal
