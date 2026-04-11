@echo off
REM Default `py` may be 3.14 while `pip install` targeted 3.13 — use 3.13 where deps live.
py -3.13 "%~dp0run_v.py" %*
