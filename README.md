# Tanzquotient (TQ) Website

The website is built using Django, and uses redis for caching and celery as a
task queue.

Users can find a user documentation [here][RTD-user].

The main repository lives on the [ETH Gitlab][eth-gitlab] and is
mirrored to [Github][github].

The repository contains the needed configurations to deploy to [SIP][sip].

## Local Setup

1. Make sure [Docker][docker] is installed.
2. Clone this repo: `git clone <repo-url>`
3. Create a python environment using python `>= 3.9`. You can for example set it up with
   a [venv](https://docs.python.org/3/library/venv.html).
5. Initialize the project: `./scripts/initialize_project.sh`
6. Run the project: `python manage.py runserver`
7. Find the website at [localhost:8000][local_instance]

### Using Intellij or PyCharm

Useful resources:

* [Configure an interpreter using Docker Compose][intellij-docker-compose]
* [Run/Debug Configuration: Django Server][intellij-run-django]

## Configuration

All configuration lives in an environment file: `.env`.
The following elaborate scheme of scripts is used to generate it.

The file `variables.yml` is the single source of truth by defining **all** environment variables needed for this project
to run.
The file is checked into the git repository.
**Do not modify** `variables.yml` unless you want to define new env variables or remove outdated ones.

The file `overrides.yml` contains custom values for your setup.
A basic version will be generated when initializing the project.
This file is ignored by git.
**Do not add it to the repository**.
The file is machine specific and could potentially contain secrets.

Both need to be of the following form:

```yaml
# General form for an entry
<NAME_OF_VARIABLE>: <value>

# Example
COMPOSE_FILE: docker-compose.yml
TQ_DEBUG: true
```

### Generate Environment

Run `./scripts/generate_env.py [--sip] [--overrides FILE]` to generate the environment.

* Without arguments it will create a `.env` file for Docker Compose and Django to use.
* `--sip` will read the variables provided by [SIP][sip] and create a `.env` file
* To use a different overrides file specify `--overrides`

## Documentation

There is a not-quite-up-to-date documentation at [ReadTheDocs][RTD].


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

[tq-it-mail]: mailto:informatik@tanzquotient.org

[django-docs]: https://docs.djangoproject.com/en/2.2/

[intellij-docker-compose]: https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#configuring-docker

[intellij-run-django]: https://www.jetbrains.com/help/idea/run-debug-configuration-django-server.html
