
@echo off
echo Testing Admin Password Protection...

:: 1. Test Chat Endpoint WITHOUT password (should fail 403)
echo [TEST 1] Chat without password
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" -d "{\"message\": \"hi\"}" ^
  -w "%%{http_code}" -s -o NUL
echo.

:: 2. Test Chat Endpoint WITH WRONG password (should fail 403)
echo [TEST 2] Chat with wrong password
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" -d "{\"message\": \"hi\"}" ^
  -H "x-admin-password: wrong" ^
  -w "%%{http_code}" -s -o NUL
echo.

:: 3. Test Chat Endpoint WITH CORRECT password (should pass 200 - assumes server is running with 'change-me')
echo [TEST 3] Chat with correct password
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" -d "{\"message\": \"hi\"}" ^
  -H "x-admin-password: change-me" ^
  -w "%%{http_code}" -s -o NUL
echo.
