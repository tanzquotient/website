Unit Tests
==========

This project uses unit tests to guarantee correctness of the code and make it easier to update dependencies without breaking anything.

General rule
------------

Whenever a new feature is implemented, the corresponding unit tests should also be written. The list below should be updated.

How to run tests
----------------

The tests can be run by invoking :code:`scripts/run_tests.sh` from the project root directory. The test database is generated the first time you run the script and kept in order to speed up the test execution.

**This means that you have to call** :code:`scripts/delete_test_database.sh` **whenever a model changes because the test database is not synchronized with the code!**

Parts of the code for which tests exist
---------------------------------------

Currently, there are no tests.

Test environment
----------------

Some testing data is stored in so called fixtures. The most important data is:

Root user:
~~~~~~~~~~

name: root

password: root

Test users:
~~~~~~~~~~~

- name: Max Mustermann

  password: testtest
  
  email: example@host.com

- name: Maxima Musterfrau

  password: testtest
  
  email: example_2@host.com
