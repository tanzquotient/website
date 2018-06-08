Certificate renewal
===================

The live server uses `<https://letsencrypt.org>`_ to provide secure, HTTPS connections. Every 3 months, the certificates expire and must be renewed. Ideally this is done by a cronjob, however due to Issue #114 this is not working at the moment. The procedure to renew the certificate is:

- Stop the live server:

.. code-block:: bash

      cd tq_website
      docker-compose stop

- Renew certificates:

.. code-block:: bash

       certbot renew

- Start the live server again:

.. code-block:: bash

       docker-compose up -d

- Check the logs and make sure everything is running as expected.
- Enjoy a cup of coffee.
