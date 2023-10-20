#!/bin/sh

while ! nc -z db 3306;
do
    echo "Waiting for the MySQL Server"
    sleep 3
done
echo "Bot is running..."
python3 app.py
