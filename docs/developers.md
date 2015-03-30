# For developers

This page contains information for developers of the website. A [user manual](index.md) is separately available.

## Additional Icons:
[Font-Awesome](http://fortawesome.github.io/Font-Awesome/icons/)
 
## Instructions for server setup

### Basic stuff
[nginx, supervisor, gunicorn](http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/)

### for sending mails asynchronously
[post_office plugin + celery](http://scanova.io/blog/engineering/2014/05/05/asynchronous-email-sending-using-django-post_office-celery/)

Note that we use MySQL instead of Postgres

## Commands:

### Data related commands

	python manage.py migrate
	python manage.py fill

easier but more dangerous: resetting *everything*, including database content!

	fab local_reset

### Servers

Run message passing server RabbitMQ

	sudo rabbitmq-server
	
Run local test server:

	python manage.py runserver

Run celery:

	python manage.py celeryd

Note: *In production* the setting is a bit different:

* a dedicated application server called gunicorn is used instead of the Django development server and run via supervisor:

	sudo supervisorctl restart tq_website
	
* as a webserver nginx is used:

	sudo service nginx restart

* and celery is also run via supervisor


	

## Installation:

Install the following packages with `sudo apt-get install ...`

	virtualenv
	pip
	mysql
	libmysqlclient-dev
	python-dev
	gcc
	gcc-multilib
	rabbitmq-server // used by celery (and celery is used by post_office)
	libjpeg-dev // used by pillow for image handling

maybe reinstall if already installed without libjpeg-dev

	pip install -I pillow

Strange, but we have to separately migrate ckeditor

	manage.py migrate djangocms_text_ckeditor



### Inside virtualenv (as root)

#### Maybe remove all packages first

If the virtualenv is not freshly created and there are already packages installed, remove them with

	pip freeze | xargs pip uninstall -y
	
NOTE: this is better then deleting and recreating the virtualenv because it preserves other virtualenv configuraitons.
	
#### Install packages

	pip install mysql-python // without sudo!!!

or

	pip install -r requirements.txt
	
to install all at ones from requirements file (recommended).

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
