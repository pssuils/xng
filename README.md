Installation
============

 * Python 2.7
 * setuptools

 Run `sudo python setup.py install`

Functionality
=============
{{{
Usage: xng.py [options]

Options:
  -h, --help            show this help message and exit
  -d DIR, --dir=DIR     path to the directory of the images, is mandatory
  -f FRAME, --frame=FRAME
                        frame duration in milliseconds
  -k KEYFRAME, --keyframe=KEYFRAME
                        rate for keyframe refreshing
  -t THRESHOLD, --threshold=THRESHOLD
                        similiraty to consider on the compression between 0
                        and 1
  -o OUT, --out=OUT     name of the file which will contain the result, is
                        mandatory


}}}



xng.py generates a xng file based on a folder containing a set of images (tested with pngs but it should work with other formats). It is possible to achieve a bit of compression using two parameteres KEYFRAME and THRESHOLD. The algorithm compares a sequence of images to a keyframe and sets the pixels that differ less than THRESHOLD to 0 and alpha channel to 0 (transparent) allowing to the png algorithm to be a bit more efficient in those frames. 
