==========
Benchmarks
==========
If you are using reck types in time critical code you will be interested in the
speed benchmarks described in this section. The tests compare reck types
with named tuples.

The tests
=========
All the benchmarks were carried out for records containing 5 fields, using
the timeit module in Python 3.4 (CPython), running under Windows 7 on a
Hewlett Packard Intel i7 laptop, operating on mains power (yes, that can make
a big difference!). All times are the best of three attempts. The relative
timings should not be treated as definitive since they will likely vary with
hardware and Python interpreter used, but should give a rough idea of
relative performance. The code statement provided to ``timeit.timeit()`` for
each test are given below.

Timing of instantiation was carried out by passing field values as positional
arguments and as keyword arguments. The statements tested were:

    1. Values by position: ``r = R(0, 1, 2, 3, 4)``
    2. Values by keyword: ``R(f0=0, f1=1, f2=2, f3=3, f4=4)``

where R is either a namedtuple or a recktype.

Getting and setting a single field by named attribute and integer index was
tested as follows:

    1. Get value by attribute: ``r.f0``
    2. Get value by index: ``r[0]``
    3. Set value by attribute: ``r.f0 = 9`` for a reck type and
       ``r = r._replace(f0=9)`` for anamed tuple (due to immutability of named
       tuples)
    4. Set value by index: ``r[0] = 9`` (for reck only due to immutability
       of named tuples)

where r is an instance of a reck type or named tuple (where possible).

Finally, the updating of multiple fields was assessed by updating the values
of 3 fields with the following code statements:

    1. reck: ``r._update(f0=6, f1=7, f2=8)``
    2. reck: ``r.f0 = 6; r.f1 = 7; r.f2 = 8``
    3. named tuple: ``r = r._replace(f0=6, f1=7, f2=8)``

where r is an instance of a recktype or namedtuple.

Results
=======
=============================  ==========  ==========  ============  ========================
Benchmark results                          Execution time (s)
-----------------------------  ----------  ------------------------  ------------------------
Test                           Iterations  namedtuple  reck          X faster than namedtuple
=============================  ==========  ==========  ============  ========================
Instantiate (positional args)  1.0e+05      0.06       0.43           0.14
Instantiate (keyword args)     1.0e+05      0.09       0.47           0.19
Get value by attribute         1.0e+07      0.92       0.43           2.14
Get value by index             1.0e+07      0.47       5.61           0.08
Set value by attribute         1.0e+07     22.14       0.50          44.28
Set value by index             1.0e+07       n/a       6.39            n/a
Update multiple field values   1.0e+05      0.24       0.26 (0.02*)   0.92 (12.0*)
=============================  ==========  ==========  ============  ========================
| * using multiple set-by-attribute statements instead of ``_update()``

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

