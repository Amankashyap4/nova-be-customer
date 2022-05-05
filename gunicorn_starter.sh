#!/bin/sh

flask db upgrade

gunicorn app.wsgi:app -b 0.0.0.0:5000 --worker-class gevent --log-level error --error-logfile - --access-logfile -
