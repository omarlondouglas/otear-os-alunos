git fetch origin > debug_push.txt 2>&1
echo "--- UNPUSHED COMMITS ---" >> debug_push.txt
git log origin/main..HEAD --oneline >> debug_push.txt 2>&1
echo "--- SUBMODULE STATUS ---" >> debug_push.txt
git submodule status >> debug_push.txt 2>&1
echo "--- REMOTE URL ---" >> debug_push.txt
git remote -v >> debug_push.txt 2>&1
