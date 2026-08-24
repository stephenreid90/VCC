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
REM /s recurses: a stale .git\refs\heads\*.lock silently defeats "git branch -D"
REM and blocks the bundle fetch. This bit us on 24 August 2026.
del /s /q "%~dp0.git\*.lock" 2>nul
del /s /q "%~dp0.git\*.lock.dead*" 2>nul
REM engine_workbook.py standalone-run artifact (gitignored; only created when the module is run directly)
del /q "%~dp0ui_prototypes\_generator\_dnl_full.xlsx" 2>nul
del /q "%~dp0ui_prototypes\_generator\_wbc_full.xlsx" 2>nul
del /q "%~dp0ui_prototypes\_generator\_csl_full.xlsx" 2>nul
REM stray loose-object temp files git push could not unlink under the mount
for /d %%D in ("%~dp0.git\objects\*") do del /q "%%D\tmp_obj_*" 2>nul
del /q "%~dp0.git\objects\pack\tmp_*" 2>nul
echo Sandbox cleanup complete.
