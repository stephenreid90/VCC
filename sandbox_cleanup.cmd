@echo off
REM ============================================================================
REM  sandbox_cleanup.cmd  -  clears files the Cowork sandbox orphans.
REM
REM  The Cowork mount permits file CREATE but not DELETE, so each session leaves
REM  behind: generator *.bak backups and .git\*.lock.dead* files (locks moved
REM  aside during commit/push). This script deletes them from a normal cmd window.
REM  Safe to run any time no git operation is in progress. Double-click or run:
REM      sandbox_cleanup.cmd
REM ============================================================================
del /q "%~dp0ui_prototypes\_generator\*.bak" 2>nul
del /q "%~dp0.git\*.lock.dead*" 2>nul
del /q "%~dp0.git\*.lock" 2>nul
echo Sandbox cleanup complete.
