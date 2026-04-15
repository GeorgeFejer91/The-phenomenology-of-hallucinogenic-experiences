@echo off
setlocal enabledelayedexpansion
:: One-click preprint build. Compiles Preprint/main.tex into Preprint/build/main.pdf
:: and copies the result up to Preprint/main.pdf for easy access.

set "SCRIPT_DIR=%~dp0"
set "PREPRINT_DIR=%SCRIPT_DIR%Preprint"
set "BUILD_DIR=%PREPRINT_DIR%\build"
set "MAIN_TEX=main.tex"
set "MAIN_PDF=main.pdf"

if not exist "%PREPRINT_DIR%\%MAIN_TEX%" (
  echo Cannot find %PREPRINT_DIR%\%MAIN_TEX%.
  pause
  exit /b 1
)

pushd "%PREPRINT_DIR%"

where latexmk >nul 2>nul
if %ERRORLEVEL%==0 (
  echo Building with latexmk...
  latexmk -pdf -bibtex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build "%MAIN_TEX%"
  set "EXITCODE=!ERRORLEVEL!"
) else (
  echo latexmk not on PATH. Falling back to pdflatex / bibtex pipeline.
  if not exist build mkdir build
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build "%MAIN_TEX%"
  if !ERRORLEVEL! NEQ 0 ( set "EXITCODE=!ERRORLEVEL!" & goto :build_done )
  pushd build
  bibtex main
  popd
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build "%MAIN_TEX%"
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build "%MAIN_TEX%"
  set "EXITCODE=!ERRORLEVEL!"
)

:build_done
if exist "%BUILD_DIR%\%MAIN_PDF%" (
  copy /Y "%BUILD_DIR%\%MAIN_PDF%" "%PREPRINT_DIR%\%MAIN_PDF%" >nul
  echo.
  echo Build OK. PDF at %PREPRINT_DIR%\%MAIN_PDF%
) else (
  echo.
  echo Build did not produce %BUILD_DIR%\%MAIN_PDF%.
  set "EXITCODE=1"
)

popd
if not "%EXITCODE%"=="0" pause
exit /b %EXITCODE%
