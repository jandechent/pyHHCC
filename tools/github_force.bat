cd ..
cd docs/sphinx-engine
sphinx-build -b html . ../html
sphinx-build -b markdown . ../markdown
cd ../..

git checkout --orphan temp_branch
git add -A
git commit -am "update"
git branch -D master
git branch -m master
git push -f origin master