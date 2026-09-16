@echo off
echo Starting AGI Services...

start "API Gateway" cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
start "Video Service" cmd /k "cd agi-videos-temp && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"
start "Carousel Service" cmd /k "cd carrocel/backend && set PORT=8002 && python main.py"

echo Services started!
echo Gateway: http://localhost:8000
echo Video Service: http://localhost:8001
echo Carousel Service: http://localhost:8002
