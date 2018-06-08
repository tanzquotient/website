========================================================
Tips when working on the production server [Admin only]:
========================================================
- **Always perform a backup before you change something on the server!!!** The scripts responsible for this can be found in the parent directory of the source code directory on the server.
  
  - :code:`mysql-backup.sh`: Performs a full dump of all databases. Then it encrypts the dump, removes the unencrypted directory and uploads the encrypted backup to the VSETH cloud.
  - :code:`mysql-backup-tq_website.sh`: Performs a backup of the tq_website database. **The backup is neither encrypted nor uploaded to the cloud!**

- **Never ever use** :code:`docker-compose down` **!!!** This will "delete" the database! Use :code:`docker-compose stop` and :code:`docker-compose start` or :code:`docker-compose restart` instead.
