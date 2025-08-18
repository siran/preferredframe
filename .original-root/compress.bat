REM FOR /F "TOKENS=1 eol=/ DELIMS=/ " %%A IN ('DATE/T') DO SET dd=%%A
REM FOR /F "TOKENS=1,2 eol=/ DELIMS=/ " %%A IN ('DATE/T') DO SET mm=%%B
REM FOR /F "TOKENS=1,2,3 eol=/ DELIMS=/ " %%A IN ('DATE/T') DO SET yyyy=%%C

@echo off
For /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
For /f "tokens=1-2 delims=/:" %%a in ("%TIME%") do (set mytime=%%a%%b)
set fname=fotos-%mydate%_%mytime%.7z
set zipped="C:\Users\Hp_user\Documents\tobo-zipped\%fname%"
7z a -mx1 -sdel %zipped% "C:\Users\Hp_user\Documents\tobo-unzipped\*"
move %zipped% C:\Users\Hp_user\Documents\MEGA\tobo\

pause

