#!/bin/sh

flask db upgrade

gunicorn --worker-class gevent --workers 4 --timeout 1000 -b 0.0.0.0:5000 --log-level error --error-logfile - --access-logfile -  app.wsgi:app
