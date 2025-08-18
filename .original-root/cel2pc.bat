@echo off
set TRIES=1000
set INTERVAL=120
 
:retry

:: Transfiriendo archivos
echo Transfiriendo archivos del cel al compu (borrando en el cel luego de transferido)
REM /log="C:\Users\Hp_user\Documents\MEGA\michelson\transferlogs\transfer.log"
WinSCP.COM /ini=nul /script="C:\Users\Hp_user\Documents\MEGA\scripts\cel2pc_winscp_script.txt" /logsize=1M /loglevel 0

:: Generando comprimido :::::::::::::::::::::::
REM echo Comprimiendo fotos y descartando fotos luego de compresion...
REM For /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%b-%%a)
REM For /f "tokens=1-2 delims=/:" %%a in ("%TIME%") do (set mytime=%%a%%b)
REM set fname=fotos-%mydate%_%mytime%.7z
REM set zipped="C:\Users\Hp_user\Documents\tobo-zipped\%fname%"
REM 7z a -mx1 -sdel %zipped% "C:\Users\Hp_user\Documents\tobo-unzipped\*"

REM echo Moviendo comprimido a carpeta de transferencia...
REM move %zipped% C:\Users\Hp_user\Documents\MEGA\tobo\
:::::::::::::::::::::::::::::::::::::::::::::::

REM move "C:\Users\Hp_user\Documents\tobo-zipped\*" C:\Users\Hp_user\Documents\MEGA\tobo\
REM move "C:\Users\Hp_user\Documents\tobo-unzipped\*" C:\Users\Hp_user\Documents\MEGA\tobo\
echo -------------------------------
echo ""
echo Esperando 30m ... (usando PING)
echo Hora actual:
date /T
time /T
ping 99.99.99.99 -n 1 -w 1800000

goto retry
 
REM if %ERRORLEVEL% gtr 1  (
   REM set /A TRIES=%TRIES%-1
   REM if %TRIES% gtr 1 (
       REM echo Failed, retrying in %INTERVAL% seconds...
       REM timeout /t %INTERVAL%
       REM goto retry
   REM ) else (
       REM echo Failed, aborting
       REM exit /b 1
   REM )
REM ) else (
    REM echo Error, %ERRORLEVEL%
REM )
 
REM echo Success
REM exit /b 0