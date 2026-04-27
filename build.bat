@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo Building executable... note: you must have the Data/ folder present.
pyinstaller tanukora.spec
echo Done.
pause
