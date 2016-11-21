#!/usr/bin/env python3
'''vprint.py
   Define debug level.
   From the command line specify the verbosity (default=0): demo.py input/easy.txt <verbosity, one of -v0, -v1, -v2, -v3>
   Example: demo.py input/easy.txt -v2
   Import for use as: from vprint import vprint
   Use as: vprint(<level>, *args_to_print, sep=<separator string, default=' '>, end=<end string, default='\n'>)
   CSC456, Fall 2016
   Author: David Shumway
'''
import sys
DEBUG_LEVEL_=0

for arg in sys.argv:
 if arg=='-v0' or arg=='-v1' or arg=='-v2' or arg=='-v3':
  a=int(arg.replace('-v',''))
  DEBUG_LEVEL_=int(a)	# 0=Show only 0-level prints
			# 1=Show 1-level and below prints (0,1)
			# 2=Show 2-level and below prints (0,1,2)
			# 3=Show 3-level and below prints (0,1,2,3)
if DEBUG_LEVEL_>0:
 print('DEBUG_LEVEL_ on:',DEBUG_LEVEL_)

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
  
if __name__=='__main__':
 pass
