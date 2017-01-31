# Server setup, configuration and maintenance

This file contains setup with docker. Earlier a [manual setup](setup_virtualenv.md) was used. Many of the manual steps are now described in the `Dockerfile`.

The setup instructions are divided into:

* common steps for all setups

* steps for local development

* steps only necessary on the production server

The following picture sketches the setup. Some notes:

* Deployment is done by logging in to the server via SSH and pulling the (production-)branch from the repository

* The python environment is configured the same locally and on the server.

* On the server a faster and more secure web server (nginx) is used instead of the Django development server

* Some secrets (config file with login information, secret keys) are not synchronized via the repository. This secrets also differ from the one used on development machines.

![Webstack](webstack.svg)

## Setup basic tools

You can use [git](https://git-scm.com/) for code management and [Docker](//www.docker.com) for setup automation.

We use a standard `Debian 8` on the server. On development machines, any operating system can be used in principle. The instructions here are compiled for a **Debian/Ubuntu** installation.

First update your system:

```shell
sudo apt-get update
sudo apt-get upgrade
```

*NOTE*: Package names can deviate depending on your Linux distribution.

```shell
sudo apt-get install git mysql-client
```

We need [docker-engine](https://docs.docker.com/engine/installation/linux/ubuntulinux/) and [docker-compose](https://docs.docker.com/compose/install/). With prerequisites satisfied, it boils down to

```shell
sudo apt-get install docker-engine
sudo curl -L https://github.com/docker/compose/releases/download/1.7.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### IDE

Install a local IDE. We highly recommend to use [PyCharm](https://www.jetbrains.com/pycharm/). The full version has Django support and is free for educational purposes.

To get the educational version, go to [PyCharm Student](https://www.jetbrains.com/shop/eform/students) and fill out the form using an official @ethz.ch mail address. After completing, you will receive an e-mail from JetBrains with a link to confirm your request. If all works well, you will receive another e-mail with further instructions on how to set up a JetBrains user account.

Finally you can download PyCharm Professional Edition, extract it and place it somewhere you want. There is no installation required. To start the program run `<YourPyCharmFolder>/bin/pycharm.sh`.

Activation is easiest if you download the licence-file from your JetBrains account-page. When asked for activation, simply drag&drop the file into the activation-key textbox.


## Setup local files

### Pull files with git

Create a folder on your machine where you want to store the local copy of the repository. This could e.g. be in your home directory.

```shell
mkdir ~/Projects/<project home>
```

Now cd into the newly created folder

```shell
cd ~/Projects/<project home>
```

and execute the following commands to tell git that your local copy of the repository now lives in this folder.

```shell
git init
git remote add origin https://github.com/gitsimon/tq_website.git
git fetch
git checkout -t origin/master
```

### Initial Configuration

We have to create 2 files manually.

First create a file `<project home>/maintenance.config` in the root folder of the project with the content

```shell
set $maintenance 0;
```

Alternatively you can just execute the script `./scripts/stop_maintenance.sh` which will also create file if it does not exist.

(Whenever doing maintance, switch this flag to 1 (and back again), and restart docker-compose to make nginx reload this config)

Create the *secret* config file in the folder `<project home>/tq_website/settings_local.py`.
This file is not under version control because it contains some secrets.
Add something along these lines, replace all stars `****` with appropriate secrets:

```python
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '****'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SSLIFY_DISABLE = True

# Configure the email host to send mails from
EMAIL_HOST = 'mailsrv.vseth.ethz.ch'
EMAIL_HOST_USER = 'informatik@tq.vseth.ch'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = '****'
DEFAULT_FROM_EMAIL = 'informatik@tq.vseth.ch'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'db',
        'NAME': 'tq_website',
        'USER': 'root',
        'PASSWORD': 'root',
    }
}
```

On the server with SSL change these lines to
```python
DEBUG = False
SSLIFY_DISABLE = False
```

*Attention*: The configured mail account is used to - depending on the action - send huge amounts of auto-generated mails. Configure a test mail server before starting the `celery` task that sends out mails.


## Let Docker do the hard part for you!

**On development machine**:
Simply run
	``docker-compose up``
in the `tq_website` directory. It will fetch all required dependencies (except `settings_local.py` and the database setup previously) and start the development server on port 8000.

**In production environment**:
To setup a production environment you can simply run ``docker-compose -f docker-compose-production.yml up``.

## Get Data

Get in touch with admin to get a backup of live database (with removed personal data).
The backup can then be applied to the database with (while docker is running the containers)

```shell
mysql -h 127.0.0.1 --port=3309 -u root -proot -t tq_website < database_backup.sql
```
	



	
At this point setup is finished and you should be able to view the local website at `127.0.0.1:8000`. Congratulations!

    
    
## Apply code changes
Pull the changes from the correct branch (here the master):

```shell
git pull
```

Apply migrations

```shell
./django-admin migrate
```
