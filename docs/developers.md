# For developers

This page contains information for developers of the website. A [user manual](index.md) is separately available.

## Additional Icons:
[Font-Awesome](http://fortawesome.github.io/Font-Awesome/icons/)
 
 
## Commands:

	python manage.py migrate
	python manage.py fill

easier but more dangerous: resetting *everything*, including database content!

	fab local_reset

Run local test server:

	python manage.py runserver


## Installation:

Install the following packages with `sudo apt-get install ...`

	virtualenv
	pip
	mysql
	libmysqlclient-dev
	python-dev
	gcc
	gcc-multilib



### Inside virtualenv (as root)

	pip install mysql-python // without sudo!!!

or

	pip install -r requirements.txt

## Setup


### virtualenv

	create virtualenv env


### Git


	git init
	git remote add origin PATH/TO/REPO
	git fetch
	git checkout -t origin/master

if wrong path (only https works without public key) -> change with:

	git remote set-url origin git://new.url.here

## Read the docs

For full documentation visit [mkdocs.org](http://mkdocs.org).

### Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs help` - Print this help message.

### Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
