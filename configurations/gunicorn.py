# Gunicorn configuration file

# Server Socket
bind = '0.0.0.0:29000'

# Worker Processes
workers = 3

# Workers silent for more than this many seconds are killed and restarted.
timeout = 300

# Chdir to specified directory before apps loading
chdir = '/webapps/tq_website'

# Restart workers when code changes.
reload = False


# Logging

# The Error log file to write to
# '-' means log to stdout
errorlog = '-'

# The Access log file to write to
# '-' means log to stdout
accesslog = '-'

# The granularity of Error log outputs
# Valid level names are: debug, info, warning, error, critical
loglevel = 'info'


