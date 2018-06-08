Translations
============

Related documentation
---------------------

Use the :code:`trans` tag in HTML sites for django:
`<https://docs.djangoproject.com/en/1.10/topics/i18n/translation/#trans-template-tag>`_

What to do
----------
Essentially, you have to run two scripts:

.. code-block:: bash

    scripts/makemessages.sh
    scripts/compilemessages.sh

Mac: install gettext
--------------------
#. :code:`brew install gettext` in Terminal and then 
#. :code:`brew link gettext --force` to make it work ;)


Manual way (deprecated for our project)
---------------------------------------

Run :code:`django-admin makemessages -a` to create the .po files. 
*Note*: Works only with :code:`gettext` installed, see below for installation

Then after you've updated the German text in the .po file you can run

.. code-block:: bash

    django-admin compilemessages

to compile the language files.

Check in the language files to git as well, we don't compile a second time on the live server.

**Please use English as the default language and then add German translations.**

Generate new binary files (.mo) after changing ASCII file (.po) 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    docker-compose run --rm django python3 manage.py compilemessage
