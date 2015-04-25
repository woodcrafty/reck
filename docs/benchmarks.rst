==========
Benchmarks
==========
If you are using reck types in time critical code you will be interested in the
speed benchmarks described in this section. The tests compare reck types, named
tuples and dictionaries.

The tests
=========
All the benchmarks were carried out for records containing 5 fields, using
the timeit module with 1000000 repetitions, in Python 3.4 (CPython), running
under Windows 7 on a Hewlett Packard Intel i7 laptop, operating on mains power
(yes, that can make a big difference!). All times are the best of three
attempts. The relative timings should not be treated as definitive since they
will likely vary with hardware and Python interpreter used, but should give a
rough idea of relative performance. The code statements provided to
``timeit.timeit()`` for each test are given below.

Timing of instantiation was carried out by passing field values as positional
arguments and as keyword arguments. The statements tested were:

    1. Values by position: ``r = R(0, 1, 2, 3, 4)`` for reck and named tuple
       (N/A for dict).
    2. Values by keyword: ``r = R(f0=0, f1=1, f2=2, f3=3, f4=4)`` for reck and
       named tuple and ``d = dict(f0=0, f1=1, f2=2, f3=3, f4=4)`` for dict.

where R is either a namedtuple or a recktype.

Getting and setting a single field by named attribute and integer index was
tested with the following code statements:

    1. Get value by attribute: ``r.f0`` for reck and namedtuple, and
       ``d['f0']`` for dict.
    2. Get value by index: ``r[0]`` (N/A for dict)
    3. Set value by attribute: ``r.f0 = 9`` for reck, ``r = r._replace(f0=9)``
       for namedtuple (due to immutability) and ``d['f0'] = 9`` for dict.
    4. Set value by index: ``r[0] = 9`` (N/A for namedtuple and dict)

where r is a reck type or named tuple instance and d is a dict instance.

Finally, the setting of multiple fields was assessed by setting the values of
3 fields with the following code statements:

    1. reck: ``r._update(f0=6, f1=7, f2=8)``
    2. reck: ``r.f0 = 6; r.f1 = 7; r.f2 = 8``
    3. namedtuple: ``r = r._replace(f0=6, f1=7, f2=8)``
    4. dict: ``d['f0'] = 6; d['f1'] = 7; d['f2'] = 8``

where r is an instance of a reck type or named tuple and d is a dict instance.

Results
=======
=============================  ==========  ===========  ====  =============  =========
Benchmark results              Execution time (ms)            X faster than namedtuple
-----------------------------  -----------------------------  ------------------------
Test                           namedtuple  reck         dict  reck           dict
=============================  ==========  ===========  ====  =============  =========
Instantiate (positional args)   626        4372         n/a    0.14           n/a
Instantiate (keyword args)      911        4813         518    0.19           1.8
Get value by attribute/name      90          43          40    2.1            2.3
Get value by index               48         558         n/a    0.09           n/a
Set value by attribute/name    2246          50          55   44.9           40.9
Set value by index              n/a         640         n/a     n/a           n/a
Set multiple field value   s   2414        2612 (215*)  174^   0.92 (11.2*)  13.9
=============================  ==========  ===========  ====  =============  =========
| * using multiple set-by-attribute statements instead of ``_update()``
| ^ using multiple assignment statements of the form ``d[key] = value``

Conclusions
===========
If your use-case involves long-lived records whose use is dominated by
accessing field values by named attribute, or the data is dynamic,
then reck types offer considerable speed benefits over named tuples. However,
named tuples are immutable, which may be a desirable feature. When updating
multiple fields using reck, it is much faster to set the fields individually
by attribute rather than using the ``_update()`` method, at the cost of more
lines of code.

If the data is static and accessing fields by attribute is less frequently
required, or access by index is needed frequently, named tuples are
significantly faster than reck types. Also, if the records are short-lived,
requiring frequent instantiation, named tuples offer better performance.

