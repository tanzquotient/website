docker-compose run --rm django python3 manage.py dumpdata --indent 2 --output cms_fixture.json --exclude cms.usersettings cms
#docker-compose run --rm django python3 manage.py dumpdata --indent 2 --output courses_fixture.json --exclude=courses.userprofile --exclude=courses.bankaccount courses
