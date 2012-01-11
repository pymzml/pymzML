#!/bin/bash

## create all packages
#rm MANIFEST

## MAKE DOCU
# rm -rf Documentation/*
# mkdir Documentation

# rm -rf Documentation_src/build/html/*.html
# rm -rf Documentation_src/build/html/*.html

# rm -rf Documentation_src/build/latex
cd Documentation_src
make html latexpdf
cd ..

# setup just goes bananas with this one...
# mv compare ../


rm -rf dist/*

## PACK IT

# cp -r Documentation_src/build/html Documentation/
cp Documentation_src/build/latex/pymzml.pdf Documentation/
cp -r Documentation_src/build/html/* Documentation/html/

python setup.py sdist --formats=bztar,gztar,zip
#python setup.py bdist --formats=bztar,gztar,bztar,zip
cd dist
tar xvfj *.bz2
cd ..


mkdir Documentation/html/dist/
cp dist/pymzml*.zip Documentation/html/dist/pymzml.zip
cp Documentation_src/build/latex/pymzml.pdf Documentation/html/dist/
cp dist/pymzml*.tar.bz2 Documentation/html/dist/pymzml.tar.bz2


# moving compare back
# mv ../compare .