@echo off

@REM install pip reqs if necessary

pip list | findstr pipreqs > temp
set /p PIPREQSFOUND=<temp
del temp

if ["%PIPREQSFOUND%"]==[] (
    pip install pipreqs
)

pipreqs --encoding=utf8 .

pip install -r requirements.txt

del requirements.txt
