@ECHO off

set "mode="
set /p mode=Press Enter to continue or type "l" and enter for legacy mode (single thread)...

IF "%mode%"=="" simnibs_python MultiNeMo.py
IF "%mode%"=="l" simnibs_python GUINEMO.py

exit