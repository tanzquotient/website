Altering the database: Migrations
=================================

What are migrations for?
------------------------

Every time changes are made to a **model**, migrations have to be created and applied to the database in order to tell it that its structure has changed. Migrations also determine what happens to entries that already exist in the database. A migrations file contains SQL code that is executed in the database.

How can I create migrations?
----------------------------

In the root directory of our git directory, enter the following command in the terminal:

.. code-block:: bash

    scripts/makemigrations.sh

How can I apply migrations?
---------------------------

In the root directory of our git directory, enter the following command in the terminal:

.. code-block:: bash

    scripts/migrate.sh

WARNING
-------

Before applying migrations to the production database, **always make a backup**!!!
