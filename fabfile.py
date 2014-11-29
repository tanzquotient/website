from fabric.api import lcd, local
from fabric.context_managers import env
import os

def deploy():
    with lcd(os.path.dirname(env.real_fabfile)):
        # git
        local('git pull')
        local('python manage.py migrate')
        
        restart()
        
def reset():
    with lcd(os.path.dirname(env.real_fabfile)):
        # git
        local('git pull')
        
        local_reset()
        restart()
        
def restart():
    # switch to user tq
    local('su - tq')
    
    # restart gunicorn via supervisor
    local('sudo supervisorctl restart tq_website')
    
    # restart webserver
    local('sudo service nginx restart')
    
    # switch back to first user
    local('logout')
        
def local_reset():
    with lcd(os.path.dirname(env.real_fabfile)):
        local('mysql --user=root --password="eesseell" --execute="drop schema if exists tq_website; CREATE SCHEMA tq_website DEFAULT CHARACTER SET utf8mb4 ;"')
        local('python manage.py migrate')
        local('python manage.py fill')
        local('python manage.py fill_functions')
        local('python manage.py fill_faq')