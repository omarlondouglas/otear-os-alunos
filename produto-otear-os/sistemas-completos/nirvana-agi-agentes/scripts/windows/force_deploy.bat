@echo off
echo ==========================================
echo FORCANDO DEPLOY PARA GITHUB
echo ==========================================
echo 1. Adicionando todos os arquivos...
git add .

echo.
echo 2. Commitando mudancas...
git commit -m "Deploy: Force update of backend and frontend files"

echo.
echo 3. Enviando para o GitHub (Main)...
git push origin main

echo.
echo ==========================================
echo PROCESSO FINALIZADO
echo Verifique se houve erros acima.
echo ==========================================
pause
