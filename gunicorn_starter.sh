#!/bin/sh

flask db upgrade

#gunicorn app.wsgi:app -b 0.0.0.0:5000 --log-level error --error-logfile - --access-logfile -

gunicorn app.wsgi:app -b 0.0.0.0:5000 --workers 4 --timeout 120 --worker-class gevent --log-level error --error-logfile - --access-logfile -
