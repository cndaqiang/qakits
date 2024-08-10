rm ./dist/*
python setup.py sdist
python -m pip install ./dist/$( ls ./dist/*)
#twine upload dist/*
