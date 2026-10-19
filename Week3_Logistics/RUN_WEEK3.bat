@echo off
setlocal
cd /d "%~dp0"
echo WEEK 3 - SIMULATED LOGISTICS ANALYSIS
echo [Setup] Checking Python and preparing a local environment...
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 -m venv .venv
if errorlevel 1 goto failed
goto envready
:usepython
where python >nul 2>nul
if errorlevel 1 goto nopython
python -m venv .venv
if errorlevel 1 goto failed
:envready
".venv\Scripts\python.exe" -c "import sys; assert sys.version_info >= (3,11), 'Python 3.11 or newer required'"
if errorlevel 1 goto failed
echo [Dependencies] Installing the tested library versions...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo [Tests] Running 15 checks...
".venv\Scripts\python.exe" -m unittest discover -s tests -v
if errorlevel 1 goto failed
echo [Analysis] Generating data, tables and eight charts...
".venv\Scripts\python.exe" run_week3.py
if errorlevel 1 goto failed
echo.
echo SUCCESS. Open results\figures for the charts.
echo The supplied Word report already contains these default-seed results.
pause
exit /b 0
:nopython
echo Install Python 3.11 or newer from python.org and enable Add Python to PATH.
pause
exit /b 1
:failed
echo A step failed. Keep this window open and read or screenshot the error above.
echo No submission has been sent.
pause
exit /b 1
