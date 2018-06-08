===============
Common Problems
===============

One of the migrations fails
===========================

Problem
-------
During migrations, an error message similar to the one below is printed:

.. code-block:: bash

    Traceback (most recent call last):
      File "manage.py", line 10, in <module>
        execute_from_command_line(sys.argv)
      File "/usr/local/lib/python3.5/site-packages/django/core/management/__init__.py", line 367, in execute_from_command_line
        utility.execute()
      File "/usr/local/lib/python3.5/site-packages/django/core/management/__init__.py", line 359, in execute
        self.fetch_command(subcommand).run_from_argv(self.argv)
      File "/usr/local/lib/python3.5/site-packages/django/core/management/base.py", line 294, in run_from_argv
        self.execute(*args, **cmd_options)
      File "/usr/local/lib/python3.5/site-packages/django/core/management/base.py", line 345, in execute
        output = self.handle(*args, **options)
      File "/usr/local/lib/python3.5/site-packages/django/core/management/commands/migrate.py", line 204, in handle
        fake_initial=fake_initial,
      File "/usr/local/lib/python3.5/site-packages/django/db/migrations/executor.py", line 115, in migrate
        state = self._migrate_all_forwards(state, plan, full_plan, fake=fake, fake_initial=fake_initial)
      File "/usr/local/lib/python3.5/site-packages/django/db/migrations/executor.py", line 145, in _migrate_all_forwards
        state = self.apply_migration(state, migration, fake=fake, fake_initial=fake_initial)
      File "/usr/local/lib/python3.5/site-packages/django/db/migrations/executor.py", line 244, in apply_migration
        state = migration.apply(state, schema_editor)
      File "/usr/local/lib/python3.5/site-packages/django/db/migrations/migration.py", line 129, in apply
        operation.database_forwards(self.app_label, schema_editor, old_state, project_state)
      File "/usr/local/lib/python3.5/site-packages/django/db/migrations/operations/models.py", line 96, in database_forwards
        schema_editor.create_model(model)
      File "/usr/local/lib/python3.5/site-packages/django/db/backends/base/schema.py", line 295, in create_model
        self.execute(sql, params or None)
      File "/usr/local/lib/python3.5/site-packages/django/db/backends/base/schema.py", line 112, in execute
        cursor.execute(sql, params)
      File "/usr/local/lib/python3.5/site-packages/django/db/backends/utils.py", line 79, in execute
        return super(CursorDebugWrapper, self).execute(sql, params)
      File "/usr/local/lib/python3.5/site-packages/django/db/backends/utils.py", line 64, in execute
        return self.cursor.execute(sql, params)
      File "/usr/local/lib/python3.5/site-packages/django/db/utils.py", line 94, in __exit__
        six.reraise(dj_exc_type, dj_exc_value, traceback)
      File "/usr/local/lib/python3.5/site-packages/django/utils/six.py", line 685, in reraise
        raise value.with_traceback(tb)
      File "/usr/local/lib/python3.5/site-packages/django/db/backends/utils.py", line 62, in execute
        return self.cursor.execute(sql)
      File "/usr/local/lib/python3.5/site-packages/django/db/backends/mysql/base.py", line 110, in execute
        return self.cursor.execute(query, args)
      File "/usr/local/lib/python3.5/site-packages/MySQLdb/cursors.py", line 226, in execute
        self.errorhandler(self, exc, value)
      File "/usr/local/lib/python3.5/site-packages/MySQLdb/connections.py", line 36, in defaulterrorhandler
        raise errorvalue
      File "/usr/local/lib/python3.5/site-packages/MySQLdb/cursors.py", line 217, in execute
        res = self._query(query)
      File "/usr/local/lib/python3.5/site-packages/MySQLdb/cursors.py", line 378, in _query
        rowcount = self._do_query(q)
      File "/usr/local/lib/python3.5/site-packages/MySQLdb/cursors.py", line 341, in _do_query
        db.query(q)
      File "/usr/local/lib/python3.5/site-packages/MySQLdb/connections.py", line 280, in query
        _mysql.connection.query(self, query)
    django.db.utils.OperationalError: (1050, "Table 'courses_coursesuccession' already exists")


Solution
--------
- Shut down all containers: :code:`docker-compose down`
- Delete all docker containers and volumes. Delete the containers first in order to be able to delete the associated volumes. **WARNING:** This erases the entire database on your system.
  Useful commands:
  - :code:`docker container ls` to get the ID of the containers, :code:`docker container rm [ID]` to remove the container whose ID is [ID]
  - :code:`docker volume ls` to get the ID of the volumes, :code:`docker volume rm [ID]` to remove the volume whose ID is [ID]
- Start the server: :code:`docker-compose up`
- In another terminal (while the server is still running): :code:`mysql -h 127.0.0.1 --port=3309 -u root -proot -t tq_website < path/to/dump_now.sql`, where you have to set the correct path to the database dump that your IT board member gave you. Wait until this command has completed.
- Kill the server.
- Run :code:`scripts/migrate.sh` from within the folder where the TQ website code is located.
- Start the server using :code:`docker-compose up`. Your server should work fine now.
