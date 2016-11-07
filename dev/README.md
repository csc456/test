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
