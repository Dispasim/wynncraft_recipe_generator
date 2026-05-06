@echo off
setlocal
cd /d "%~dp0"
where g++ >nul 2>nul
if %errorlevel%==0 (
    g++ -O3 -std=c++17 -shared -static-libgcc -static-libstdc++ individual_cpp_backend.cpp -o individual_cpp_backend.dll
    if %errorlevel% neq 0 goto :error
    echo Backend construit: individual_cpp_backend.dll
    goto :eof
)
where cl >nul 2>nul
if %errorlevel%==0 (
    cl /O2 /EHsc /LD individual_cpp_backend.cpp /Fe:individual_cpp_backend.dll
    if %errorlevel% neq 0 goto :error
    echo Backend construit: individual_cpp_backend.dll
    goto :eof
)
echo Aucun compilateur C++ trouve. Installe MinGW g++ ou Visual Studio Build Tools.
exit /b 1
:error
echo Echec de compilation.
exit /b 1
