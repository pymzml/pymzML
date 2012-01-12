#!/bin/bash

mkdir Documentation

rm -rf Documentation/*
rm -rf Website/dist/*
rm -rf Documentation_src/build/*

# Evoke Sphinx to create html and pdf documentation
cd Documentation_src
make html latexpdf
cd ..

# Copying pdf documentation to Documentation and Website
cp Documentation_src/build/latex/pymzml.pdf Documentation/
cp Documentation_src/build/latex/pymzml.pdf Website/dist/

# Copying html documentation to Documentation and Website
cp -R Documentation_src/build/html Documentation/html
cp -R Documentation_src/build/html/* Website/

rm -rf dist/*
# Creating Python packages
python setup.py sdist --formats=bztar,gztar,zip
cd dist
tar xvfj *.bz2
cd ..

# Copying packages to Website
cp dist/pymzml*.zip     Website/dist/pymzml.zip
cp dist/pymzml*.tar.bz2 Website/dist/pymzml.tar.bz2