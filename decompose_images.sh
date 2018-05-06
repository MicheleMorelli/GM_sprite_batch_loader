#! usr/bash

# Uses Imagemagick's coalesce option to decompose a gif into several PNG frames.
# The frames are then numbered from 0

name=`echo "$1" | cut -d '.' -f1`

convert -coalesce $name.gif $name%d.png
