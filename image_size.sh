#!/bin/bash

if [ $# -ne 1 ] 
then
    [ $1 = '-w' ] && reg='s/^.*? (\d?\d?\d\d)x\d?\d?\d\d .*$/$1/i'
    [ $1 = '-h' ] && reg='s/^.*? \d?\d?\d\dx(\d?\d?\d\d) .*$/$1/i'
    file=$2 
else 
    file=$1
    reg='s/^.*? (\d?\d?\d\dx\d?\d?\d\d) .*$/$1/i'
fi

identify $1 | perl -pe "$reg"
