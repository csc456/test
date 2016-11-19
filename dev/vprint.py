#!/usr/bin/env python3
'''vprint.py
   Define debug level.
   Specify vprint(<level>, *args_to_print, sep=<separator string, default=' '>, end=<end string, default='\n'>)
'''
DEBUG_LEVEL_=3
def vprint(level,*args,**kwargs):
 '''0=Always show these ones        - stdout
    1=Sometimes show these ones     - critical
    2=Rarely show these ones        - warn
    3=Rarely Rarely show these ones - info
 '''
 s=' ' # Optional sep
 e='\n'
 for key, val in kwargs.items():
  if key == 'sep':
   s=val
  elif key == 'end':
   e=val
 if not isinstance(level, int):
  raise Exception('vprint: level must be an int!')
 if level<=DEBUG_LEVEL_:
  for i in args:
   print(i, end=s)
 print(e, end='')
  
