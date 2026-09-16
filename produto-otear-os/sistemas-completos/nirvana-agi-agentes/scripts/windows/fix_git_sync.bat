@echo off
echo STARTING GIT FIX > fix_log.txt
echo Adding gitignore... >> fix_log.txt
git add .gitignore >> fix_log.txt 2>&1
echo Removing large file... >> fix_log.txt
git rm --cached "Agente de IA para criação de conteúdo.zip" >> fix_log.txt 2>&1
echo Committing... >> fix_log.txt
git commit -m "chore: remove large zip file and update gitignore" >> fix_log.txt 2>&1
echo Pushing... >> fix_log.txt
git push origin main >> fix_log.txt 2>&1
echo DONE >> fix_log.txt
