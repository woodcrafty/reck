==========
Benchmarks
==========
If you are using recktypes in time critical code you will be interested in the
speed benchmarks described in this section.

The tests
=========
All the benchmarks were carried out for records containing 5 fields, using
the timeit module in Python 3.4 (CPython), running under Windows 7 on a
Hewlett Packard Intel i7 laptop operating on mains power (yes, that can make
a big difference!). All times are the best of three attempts. The relative
timings should not be treated as definitive since they will likely vary with
hardware and and Python interpreter used, but should give a rough idea of
relative performance. The code statement provided to ``timeit.timeit()``

Timing of instantiation was carried out by passing field values by field order
(positional arguments) and by fieldname (keyword arguments). The statements
tested were:

    1. Values by field order: ``r = R(0, 1, 2, 3, 4)``
    2. Values by fieldname: ``R(f0=0, f1=1, f2=2, f3=3, f4=4)``

where R is either a namedtuple or a recktype.

Getting and setting a single field by named attribute and integer index was
tested as follows:

    1. Get value by attribute: ``r.f0``
    2. Get value by index: ``r[0]``
    3. Set value by attribute: ``r.f0 = 9`` for recktype,
       ``r = r._replace(f0=9)`` for namedtuple (due to immutability)
    4. Set value by index: ``r[0] = 9`` (for recktyoe only due to immutability
       of naedtuples)

where r is an instance of a recktype or namedtuple (where possible).

Finally, the updating of multiple fields was assessed by updating the values
of 3 fields with the following code statements:

    1. reck: ``r._update(f0=6, f1=7, f2=8)``
    2. reck: ``r.f0 = 6; r.f1 = 7; r.f2 = 8``
    3. namedtuple: ``r = r._replace(f0=6, f1=7, f2=8)``

where r is an instance of a recktype or namedtuple.

Results
=======
=====================================  ==========  ==========  ============  ========================
Benchmark results                                  Execution time (s)
-------------------------------------  ----------  ------------------------  ------------------------
Test                                   Iterations  namedtuple  reck          X faster than namedtuple
=====================================  ==========  ==========  ============  ========================
Instantiation (values by field order)  1.0e+05      0.06       0.43           0.14
Instantiation (values by field name)   1.0e+05      0.09       0.47           0.19
Get value by attribute                 1.0e+07      0.92       0.43           2.14
Get value by index                     1.0e+07      0.47       5.61           0.08
Set value by attribute                 1.0e+07     22.14*      0.50          44.28
Set value by index                     1.0e+07       n/a       6.39            n/a
Update multiple field values           1.0e+05      0.24*      0.26 (0.02^)   0.92 (12.0)
=====================================  ==========  ==========  ============  ========================
^ using multiple set-by-attribute statements instead of _update()

Conclusion
==========
If your use-case is dominated by getting/setting field values by named
attribute, or the data is dynamic and therefore will be updated frequently,
then *reck* types offer considerable speed benefits over named tuples. However,
if the data is static and attribute lookup of fields is only occasionally
required, or access by index is frequently required, named tuples are
significantly faster than reck types.

