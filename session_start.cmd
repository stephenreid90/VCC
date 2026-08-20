@echo off
REM ===========================================================================
REM  session_start.cmd - run at the START of every session.
REM  Regenerates REPO_MAP.md and OPEN_ITEMS.html, runs the suite and the SSOT
REM  ratchet, checks the base ties, and prints git state. See CLAUDE.md.
REM ===========================================================================
python "%~dp0scripts\session_start.py" %*
