@echo off
echo ===================================================
echo Setting up TTS Testing Environment
echo ===================================================

:: 1. Check if uv is installed (recommended)
uv --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Detected 'uv' package manager. Using 'uv' for ultra-fast setup...
    
    echo Creating virtual environment...
    uv venv --python 3.12 .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment with uv.
        pause
        exit /b 1
    )
    
    echo Installing PyTorch and Torchaudio...
    uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
    if %errorlevel% neq 0 (
        echo [WARNING] CUDA-enabled PyTorch installation failed. Falling back to default PyTorch...
        uv pip install torch torchaudio
    )
    
    echo Installing f5-tts and audio processing tools...
    uv pip install f5-tts huggingface-hub soundfile librosa
    if %errorlevel% neq 0 (
        echo [ERROR] Dependency installation failed.
        pause
        exit /b 1
    )
    
    goto :success
)

:: 2. Fallback to standard Python / py launcher
echo [INFO] 'uv' not found. Falling back to standard python launcher...

:: Check py launcher
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Creating virtual environment using 'py' launcher...
    py -m venv .venv
    goto :pip_install
)

:: Check python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Creating virtual environment using 'python'...
    python -m venv .venv
    goto :pip_install
)

echo [ERROR] Neither 'uv', 'py', nor 'python' was found in your PATH.
echo Please install Python 3.9 - 3.12 and add it to your system PATH.
pause
exit /b 1

:pip_install
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing PyTorch and Torchaudio...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
if %errorlevel% neq 0 (
    echo [WARNING] CUDA-enabled PyTorch installation failed. Falling back to default PyTorch...
    pip install torch torchaudio
)

echo Installing f5-tts and audio processing tools...
pip install f5-tts huggingface-hub soundfile librosa
if %errorlevel% neq 0 (
    echo [ERROR] Dependency installation failed.
    pause
    exit /b 1
)

:success
echo ===================================================
echo Setup completed successfully!
echo To test, run: .venv\Scripts\activate
echo Then: python test_tts.py --text "नमस्ते! आप कैसे हैं?"
echo ===================================================
pause
