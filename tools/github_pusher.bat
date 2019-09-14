cd ..
cd docs/sphinx-engine
sphinx-build -b html . ../html
sphinx-build -b markdown . ../markdown
cd ../..

git add -A
git commit -am "update"
git push origin master