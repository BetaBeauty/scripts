
DEL_FILE=$1
if [[ "${DEL_FILE}" == "" ]]; then
  echo "List Large Files: "
  git verify-pack -v .git/objects/pack/*.idx | sort -k 3 -nr | head -5

  echo "File Names"
  git rev-list --objects --all | grep "$(git verify-pack -v .git/objects/pack/*.idx | sort -k 3 -nr | head -5 | awk '{print$1}')"
  exit
fi

echo "GIT Deleting ${DEL_FILE}"
git filter-branch --force --index-filter "git rm -rf --cached --ignore-unmatch ${DEL_FILE}" --prune-empty --tag-name-filter cat -- --all

echo "Push into remote"
git push origin --force --all
git push origin --force --tags

echo "Update all branch"
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all

echo "GC"
git gc --prune=now
git count-objects -v
