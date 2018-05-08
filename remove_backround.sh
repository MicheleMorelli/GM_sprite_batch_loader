#! /usr/bin/bash

#converts gif files to PNGs with no background

GIF_IMG=$1

./decompose_images.sh $GIF_IMG

for PNG_IMG in ./*.png
do
    convert $PNG_IMG -transparent 'rgb(112,204,110)' $PNG_IMG
done

#convert *png -set loop 0 -set delay 10 -set dispose previous chachacha.gif



