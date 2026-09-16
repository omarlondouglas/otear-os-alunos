@echo off
git log -n 5 --oneline > git_check.txt 2>&1
git remote -v >> git_check.txt 2>&1
echo --- TRIGGER FILE CHECK --- >> git_check.txt
dir trigger_deploy.txt >> git_check.txt 2>&1
