# Gunicorn configuration file

bind = '0.0.0.0:29000'

loglevel = 'info'
errorlog = '-'
accesslog = '-'
workers = 3