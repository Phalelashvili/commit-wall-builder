#!/bin/bash
rm -rf ~/commit-wall
mkdir ~/commit-wall
git init ~/commit-wall
git -C ~/commit-wall remote add origin git@github.com:Phalelashvili/commit-wall.git
python3.10 builder.py build ~/affix ~/commit-wall affix
python3.10 builder.py build ~/pbg ~/commit-wall pbg
gpoh --force
