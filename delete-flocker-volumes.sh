#!/bin/sh
cd /dev/rbd/rbd
for X in `ls --color=never | egrep ^flocker-`; do rbd unmap $X; done
for X in `rbd ls | egrep ^flocker-`; do rbd rm $X; done
