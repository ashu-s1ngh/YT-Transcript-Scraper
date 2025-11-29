@echo off
echo Installing PyInstaller...
pip install pyinstaller
echo.
echo Building Executable...
echo This might take a minute.
pyinstaller --noconfirm --onefile --windowed --name "YouTubeScraper" --add-data "c:/Users/Ashu/Desktop/py/Portfolio/YT video transcript scraping extension/.venv/Lib/site-packages/customtkinter;customtkinter/" gui.py
echo.
echo Build Complete!
echo You can find your app in the "dist" folder.
pause
