#!/bin/sh

while ! nc -z db 3306;
do
    echo "Waiting for the MySQL Server"
    sleep 3
done

python3 app.py
