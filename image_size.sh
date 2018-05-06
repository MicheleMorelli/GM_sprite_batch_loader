#!/bin/bash

#Gets the size of an image using ImageMagick's identify

# ./image_size.sh [OPTIONS] [IMAGE PATH]
# OPTIONS:
# -w   Returns image width
# -h   Returns image heigth

if [ $# -ne 1 ] 
then
    [ $1 = '-w' ] && reg='s/^.*? (\d?\d?\d\d)x\d?\d?\d\d .*$/$1/i'
    [ $1 = '-h' ] && reg='s/^.*? \d?\d?\d\dx(\d?\d?\d\d) .*$/$1/i'
    file=$2 
else 
    file=$1
    reg='s/^.*? (\d?\d?\d\dx\d?\d?\d\d) .*$/$1/i'
fi

identify $file | perl -pe "$reg"
