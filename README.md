gestures
========

Gestures is a lightweight tool for tracking gestures with your webcam and 
executing global commands (like volume up).


Requirements
------------
Python2 is required to run gestures.

The following non-standard libraries are required for Python:
- opencv
- ghmm
- numpy

Configuration
-------------
You can configure own gestures in the files `models.py`.
At the top, there is a section `gestures` which is defined as a list of
tuples containing the gesture and the command to be executed. The gesture
is given as a list of movements, e.g. `[UP, DOWN, UP]` and a valid
command for `subprocess`. The latter one is a list of command parts where
you split your command at spaces, i.e. `firefox -safe-mode` would become
`['firefox', '-safe-mode']`.

The complete entry would then look like this:

```python
gestures = [
    ([UP, DOWN, UP], ['firefox', '-safe-mode'])
]
```

Pay attention to the fact that there are no quotation marks around directions
like `UP` and `DOWN`, because these are special keywords by gestures.

