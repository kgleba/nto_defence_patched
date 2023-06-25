#!/bin/sh

echo "Waiting for mongodb..."

while ! nc -z mongo 27017; 
do
	sleep 0.1
done
echo "Mongodb started"

gunicorn --bind 0.0.0.0:$CONTROL_PORT -k eventlet wsgi:app
