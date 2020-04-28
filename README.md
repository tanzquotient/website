# Tanzquotient (TQ) Website

The website is built using Django, and uses redis for caching and celery as a
task queue.

Users can find a user documentation [here][RTD-user].

The main repository lives on the [ETH Gitlab][eth-gitlab] and is
mirrored to [Github][github].

The repository contains the needed configurations to deploy to [SIP][sip].


## Configuration

The `map-envvars.sh` script maps all the environment variables that the SIP
provides to the `TQ_XXX` env vars that the Django app expects (which are defined
in the .env-template).


## Local development

0. Install [Docker][docker] and [Docker Compose][docker-compose]
1. Clone this repo: `git clone <repo-url>`
2. Copy the file specifying some required environment variables into place: `cp configurations/.env-template .env`
3. Build the project in Docker: `docker-compose build --file docker-compose-dev.yml`
4. Run the project in Docker: `docker-compose up --file docker-compose-dev.yml`
5. Create minio storage buckets, see [minio docs][minio-get-started]
6. Run `./scripts/collectstatic.sh` to copy static files into storage bucket
7. Fill your database:
    * Option A: get a up-to-date database from a member of the [Tanzquotient IT team][tq-it-mail]. Restore dump locally.
    * Option B: Run `./scripts/migrate.sh` to initialize tables. Create a new superuser, see [Django docs][django-docs].
8. Find the website at [localhost:8000][local_instance]

### Using Intellij or PyCharm

Useful resources:

* [Configure an interpreter using Docker Compose][intellij-docker-compose]
* [Run/Debug Configuration: Django Server][intellij-run-django]

## Documentation
There is a not-quite-up-to-date documentation at [ReadTheDocs][RTD].


## TODOs

* redis sidecar: https://gitlab.ethz.ch/vseth/0403-isg/sip-sip-apps/sip-manager/-/issues/45
* S3 buckets: media+static accessible, postfinance private => do this in code?
* Applying migrations + collecting static files are automated for SIP, should be as well in the dev environment


[github]: https://github.com/tanzquotient/tq_website
[eth-gitlab]: https://gitlab.ethz.ch/vseth/0500-kom/0519-tq/website
[docker]: https://docs.docker.com/engine/install/
[docker-compose]: https://docs.docker.com/compose/install/
[github]: https://github.com/tanzquotient/tq_website
[sip]: https://dev.vseth.ethz.ch/
[RTD]: https://tq-website.readthedocs.io/en/latest/
[RTD-user]: https://tq-website.readthedocs.io/en/latest/introduction/non_programmer_howto.html
[minio-get-started]: https://docs.min.io/docs/minio-client-quickstart-guide.html
[local_instance]: http://localhost:8000
[tq-it-mail]: mailto:informatik@tq.vseth.ch
[django-docs]: https://docs.djangoproject.com/en/2.2/
[intellij-docker-compose]: https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#configuring-docker
[intellij-run-django]: https://www.jetbrains.com/help/idea/run-debug-configuration-django-server.html
