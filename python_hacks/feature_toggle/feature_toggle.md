# Feature toggle decorator

This is a feature toggle scheme for the system I maintain at my job. The
goal is to be able to easily toggle functions that have been recently pushed
to production, so if things go bad, we have an easy mitigation plan.

Create a database table with three columns, Key (string), Value (boolean),
LastChanged (timestamp). The purpose of the LastChanged column is just for
record keeping to decide when a feature is deemed trustworthy. The several
for a given key string present the history of switching the feature on and off,
which you can compare to the git history of the feature implementation.
To toggle the feature, add a new row to the table with the right Key, and
with LastChanged set to NOW(). Here I'm using sqlite3 for quick testing, in
the target system we use MySQL for everything.

The function get_from_db(key) does a database lookup. For the given key, it
returns the Value for the row with the latest value of LastChanged.

When you decide to trust the new feature, you remove the decorator line above
the definition of "feature_one", along with the definition of "old_behavior_one".
Until then, you can switch the feature on or off just by adding a new row to
the database table.

One thing about how the decorator is written is that it checks the database on
each invocation of the feature, as opposed to selecting the old or new behavior
just once and sticking with it. There is a performance hit in doing that but
it allows long-running processes to be left running, which is a requirement
in the target system.
