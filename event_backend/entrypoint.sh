#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Check if database is running..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py makemigrations
python manage.py migrate

#python manage.py runserver 0.0.0.0:8000
exec daphne -b 0.0.0.0 -p 8000 event_backend.asgi:application
exec "$@"
#~