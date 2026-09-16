@echo off
echo Stopping containers...
docker-compose down

echo Building containers (no cache)...
docker-compose build --no-cache

echo Starting containers...
docker-compose up -d

echo Done! Logs are available via 'docker-compose logs -f'
pause
