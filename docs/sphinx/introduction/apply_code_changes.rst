=================================
Contributing & Apply code changes
=================================

*Note*: This method of applying code changes does not destroy your test data, but gradually migrates the database.

Pull the changes from the correct branch (here the master):

.. code-block:: bash

    git pull

If you are working on your own developper branch, pull the changes of the master branch explicitely:
.. code-block:: bash

    git pull origin master

It's a good idea to rebase your branch on the master from time to time. While your branch is checked out, run:
.. code-block:: bash

    git rebase master

*Apply migrations* to your test database by entering in a shell

.. code-block:: bash

    ./scripts/migrate.sh

Then cancel (:code:`Ctrl + C`) and restart the :code:`docker-compose` command to ensure changes in configuration are reflected. Docker will detect configuration changes with that option and rebuild containers if necessary.

.. code-block:: bash

    docker-compose up --build

*Note*: If desired, see the above how to reset the database and reload a database dump. Not however, that the migrate command still has to be run because the dump can be a little outdated compared to the newest code.


Troubleshooting
---------------

What often helps
~~~~~~~~~~~~~~~~

Docker is complicate to predict. Some config files are not loaded ad-hoc. Whenever there is a problem, try to restart the containers all together with

.. code-block:: bash

    docker-compose restart

or

.. code-block:: bash

    docker-compose stop
    docker-compose up

(with the second option you will be directly attached to the containers and you see the output)

Page reload
~~~~~~~~~~~

Some assets files are cached by the browser: ensure that you make a full page reload (:code:`Ctrl + F5`) or you even delete all session cockies.
