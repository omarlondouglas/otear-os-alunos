@echo off
git remote -v > git_remote.txt 2>&1
git branch -vv > git_branch.txt 2>&1
git status > git_status.txt 2>&1
git log -n 1 > git_log.txt 2>&1
echo Done
