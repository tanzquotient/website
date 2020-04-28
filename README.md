# Tanzquotient (TQ) website

The website is built using Django, and uses redis for caching and celery as a
task queue.

Users can find a user documentation [here][RTD-user].

The main repository lives on the [ETH Gitlab][eth-gitlab] and is
mirrored to [Github][github].

The repository contains the needed configurations to deploy to [SIP][sip].


## Configuration

The `map-envvars.sh` script maps all the environment variables that the SIP
provides to the TQ_XXX env vars that the Django app expects (which are defined
in the .env-template).


## Local development

0. Install [Docker][docker] and [Docker Compose][docker-compose]
1. Clone this repo: `git clone <repo-url>`
2. Copy the file specifying some required environment variables into place: `cp configurations/.env-template .env`
3. Build the project in Docker: `docker-compose build --file docker-compose-dev.yml`
4. Run the project in Docker: `docker-compose up --file docker-compose-dev.yml`
5. Create minio storage buckets, see [minio docs][minio-get-started]
6. Collect the static files: `docker exec -it tq-django python manage.py collectstatic`
7. Apply the migrations: `docker exec -it tq-django python manage.py migrate`
8. Find the website at [localhost:8000][local_instance]

Furthermore, there is a sort-of-uptodate documentation at [ReadTheDocs][RTD].


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
