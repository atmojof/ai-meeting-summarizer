@echo off
echo ====================================================
echo ConveneAI Minutes — Meeting Summarizer ^& Analytics
echo ====================================================
echo.
echo Starting FastAPI Web Server...
echo Opening dashboard in your default browser...
echo.
start http://127.0.0.1:8000
python -m uvicorn main:app --port 8000
if %ERRORLEVEL% neq 0 (
    echo Failed to start server. Make sure Python and FastAPI dependencies are installed.
    pause
)
