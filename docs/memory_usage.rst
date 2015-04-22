============
Memory usage
============
Record objects have a low memory footprint because they store
attributes using slots rather than a per-instance dictionary. They use
significantly less memory than an equivalent dictionary and slightly less
memory (8 bytes to be precise), than an equivalent namedtuple. The example
below was executed in Python 3.4::

    >>> from reck import make_rectype
    >>> from collections import namedtuple
    >>> import sys
    >>> Rec = make_rectype('Rec', ['a', 'b'])
    >>> rec = Rec(a=1, b=2)
    >>> NT = namedtuple('NT', ['a', 'b'])
    >>> nt = NT(a=1, b=2)
    >>> dct = dict(a=1, b=2)
    >>> sys.getsizeof(rec)    # Number of bytes used by a record
    56
    >>> sys.getsizeof(nt)     # Number of bytes used by a namedtuple
    64
    >>> sys.getsizeof(dct)    # Number of bytes used by a dict
    288

These memory savings are usually not significant unless you have a very
large number of instances (e.g. hundreds of thousands), or are working on
a low memory device.
