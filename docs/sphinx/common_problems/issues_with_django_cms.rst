CKEditor does not display an option to add links and/or images:
===============================================================

Run the following lines on the server:

.. code-block:: bash

    docker-compose run --rm django python3 manage.py cms check
    docker-compose run --rm django python3 manage.py cms delete-orphaned-plugins

You have to confirm the last command manually.
