====================
Choosing a data type
====================
Believe it or not, wrecords are not always the best data type to use.
Depending on your use-case other data types may be more appropriate. This
handy table should help you choose:

+-----------------+---------+-----------+------------+------------+--------------+
| Data type       | Dynamic | Dynamic   | Per-field  | More than  | Large number |
|                 | values  | structure | defaults   | 255 fields | of instances |
+-----------------+---------+-----------+------------+------------+--------------+
| wrecord         |    Y    |     N     |     Y      |      Y     |      Y       |
+-----------------+---------+-----------+------------+------------+--------------+
| namedtuple      |    N*   |     N     |     N      |      N     |      Y       |
+-----------------+---------+-----------+------------+------------+--------------+
| SimpleNameSpace |    Y    |     Y     |     N      |      N     |      Y       |
+-----------------+---------+-----------+------------+------------+--------------+
| dict            |    Y    |     Y     |     N%     |      Y     |      N       +
+-----------------+---------+-----------+------------+------------+--------------+

* *wrecord* may be a good choice when one or more of the following are true:
    - the data has a statisc structure but dynamic values
    - per field default values (including factory function defaults) are
      required
    - the data has more than 255 fields
    - the data set consists of a very large number of instances (hundreds
      (of thousands)
* *namedtuple* are suitable if:
    - for data with a static structure and static values
  (although the ``_replace()`` method can be used to update values)
* *dictionaries* should be used when the structure of the data is dynamic, but
  memory use a very large number of instances is required.
* *SimpleNamespace* (available in in Python 3.3+) is suitable when the structure
  of the data is dynamic and attribute access is required
* classes may be needed when you need to add lots of methods to objects