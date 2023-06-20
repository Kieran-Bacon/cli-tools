@ECHO OFF
:loop
  @REM cls
  ECHO ========================================== WATCHING ==========================================
  call %*
  timeout /t 5 > NUL
goto loop