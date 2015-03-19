from fabric.api import lcd, local
from fabric.context_managers import env
import os

def deploy():
    with lcd(os.path.dirname(env.real_fabfile)):
        # git
        local('git pull')
        local('python manage.py migrate')
        
def reset():
    with lcd(os.path.dirname(env.real_fabfile)):
        # git
        local('git pull')
        
        local_reset()
        
def restart():
    # restart gunicorn via supervisor
    local('sudo supervisorctl restart tq_website')
    
    # restart webserver
    local('sudo service nginx restart')
        
def local_reset():
    with lcd(os.path.dirname(env.real_fabfile)):
        local('mysql --user=root --password="eesseell" --execute="drop schema if exists tq_cms; CREATE SCHEMA tq_cms;"')
        local('python manage.py migrate')
        local('python manage.py fill')
        local('python manage.py fill_functions')
        local('python manage.py fill_faq')