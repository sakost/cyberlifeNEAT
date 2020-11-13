# CyberlifeNEAT
it's my first cyberlife project

## Description
In my environment there is a board that has cells with food
and there are some "alive cells" that can move(not food cells).
Once a tick alive cells slowly dying(life points are taken away by some constant value).
Food is growing once a tick on some random value(from 0 to 8).
Cells can move on 4 direction(top, bottom, left, right) and they **always** eat food cells(up to 40 points).
Within a group of cells they dying slowly(like a song of Saint Asonia :) )  

## Run
* Without virtualenv
```bash
$ python -m pip install requirements.txt
$ python main.py
```
* With virtualenv
```bash
$ virtualenv venv
$ venv/bin/activate
(venv) $ python -m pip install requirements.txt
(venv) $ python main.py 
```

## Requirements
* pygame==2.0.0
* neat-python==0.92
* numpy==1.19.4

## LICENSE
mit

## Author
sakost a.k.a. Konstantin Sazhenov
