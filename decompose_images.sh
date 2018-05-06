#! usr/bin/bash

name=`echo "$1" | cut -d '.' -f1`

convert -coalesce $name.gif $name%d.png
