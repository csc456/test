# ...

Remove previous try and run demo:

```dev$ rm -rf data/*.dat data/*.txt && time ./demo3.py input/easy.txt```

Using vprint.py:

```dev$ rm -rf data/*.dat data/*.txt && time ./demo3.py input/easy.txt -v[0-3]```

Display the contents of db file in readable format.

```dev$ sort -f data/tiny-lvl3__db0___db.txt```

We may see the number of IO-wait ticks. (Per http://serverfault.com/questions/169676/howto-check-disk-i-o-utilisation-per-process.)

```cut -d" " -f 1,2,42 /proc/*/stat | sort -n -k +3 | grep python3```

Showing very low or almost no IO-wait ticks. (After all there is only file access at the start and very end of the program). Thus, you might assume that threading will not be helpful here. Yes? This is because threading comes in most handy when there is IO wait and the processor is idle. Yes?

# ...

huge-votelog.txt.try2.diff.

```
real	20m54.109s
user	20m35.802s
sys	0m13.850s
```

# ...

Running demo.py. Using try-catch to suppress errors. ```$demo.py input/big.txt```. Results in big_db-sorted.txt.

For an individual voter the structure is for example:

```
dev$ cat big_db-sorted.txt  | grep VZVGB9O
('VZVGB9O', 'E', 0)	(('Senator', 'Mary Schmidt'), None)
('VZVGB9O', 'E', 1)	1
('VZVGB9O', 'E', 2)	(('Senator', 'Harry Weasley'), None)
('VZVGB9O', 'E', 3)	(('Surgeon General', "Ronald O'Donnelly"), None)
('VZVGB9O', 'E', 4)	(('Surgeon General', "Back O'Lanterne"), None)
('VZVGB9O', 'N')	5
('VZVGB9O', 'X', ('Senator', 'Harry Weasley'))	2
('VZVGB9O', 'X', ('Senator', 'Mary Schmidt'))	0
('VZVGB9O', 'X', ('Surgeon General', "Jack O'Lanterne"))	4
('VZVGB9O', 'X', ('Surgeon General', "Ronald O'Donnelly"))	3
dev$
dev$
dev$ cat big_db-sorted.txt  | grep VTZQY7W
('T', 'E', 22)	(('President', 'George Harvey'), 2, 'VTZQY7W')
('T', 'E', 59)	(('Supreme Court Justice', 'Jack Brown'), 9, 'VTZQY7W')
('T', 'E', 61)	(('Surgeon General', 'Monica Lewinski'), 5, 'VTZQY7W')
('T', 'E', 71)	(('Mayor', 'Edgar Allen Poe'), 4, 'VTZQY7W')
('VTZQY7W', 'E', 0)	(('Supreme Court Justice', 'Ron Weásley'), None)
('VTZQY7W', 'E', 10)	(('Secretary of the Vote', 'Stoney Jabkson'), None)
('VTZQY7W', 'E', 11)	(('Governor', 'Mickey Mouse'), None)
('VTZQY7W', 'E', 12)	12
('VTZQY7W', 'E', 1)	(('Surgeon General', 'Dr. Bones'), None)
('VTZQY7W', 'E', 2)	(('President', 'George Harvey'), None)
('VTZQY7W', 'E', 3)	3
('VTZQY7W', 'E', 4)	(('Mayor', 'Edgar Allen Poe'), None)
('VTZQY7W', 'E', 5)	(('Supreme Court Justice', 'Jack Brown'), None)
('VTZQY7W', 'E', 6)	6
('VTZQY7W', 'E', 7)	(('Surgeon General', 'Monica Lewinski'), None)
('VTZQY7W', 'E', 8)	(('Governor', 'Jack'), None)
('VTZQY7W', 'E', 9)	(('Lt. Governor', 'Merlin'), None)
('VTZQY7W', 'N')	13
('VTZQY7W', 'X', ('Governor', 'Jack'))	8
('VTZQY7W', 'X', ('Governor', 'Mickey Mouse'))	11
('VTZQY7W', 'X', ('Lt. Governor', 'Merlin'))	9
('VTZQY7W', 'X', ('Mayor', 'Edgar Allen Poe'))	4
('VTZQY7W', 'X', ('Mayor', 'Robin Hood'))	6
('VTZQY7W', 'X', ('President', 'George Harvey'))	2
('VTZQY7W', 'X', ('Secretary of the Vote', 'Stoney Jackson'))	10
('VTZQY7W', 'X', ('Supreme Court Justice', 'Jack Brown'))	5
('VTZQY7W', 'X', ('Supreme Court Justice', 'Ron Weasley'))	0
('VTZQY7W', 'X', ('Surgeon General', 'Dr. Bones'))	1
('VTZQY7W', 'X', ('Surgeon General', 'Monica Lewinski'))	7
```

# ...

There is an interesting occurrence when using crusherdict.py. If you run 1,000,000 times test.getKey("Hiddleston", "name"):

```
for i in range(0,1000000):
   try:
    test.getKey("Hiddleston","name")
   except:
    pass
```

...then roughly 6,200 entries are added to the flat file "database"... which in sorted format looks like 

https://github.com/csc456/test/blob/master/dev/test_crusherdict_db-sorted-nocase.txt

What is this command doing? It checks for the key "Hiddleston" in the database; if found _____; if not found create a new key and _____. Thus across 1,000,000 attempts it is not found roughly 6,000 times. Error rate for getKey is then something like 0.006 failures per read.

# ...

Using a huge key and huge value, for example:

```
for i in range(0,1000000):
   try:
    test.getKey("Hiddleston982374987239847298347982379487239487","name982374092374092740923740923740927304239847")
   except:
    pass
```

...yields about the same number of entries in the database. That is, for 1,000,000 get requests there are 5,000 or so failed requests with a new entry created.
