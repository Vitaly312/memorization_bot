#!/bin/sh

while ! nc -z db 3306;
do
    echo "Waiting for the MySQL Server"
    sleep 3
done
echo "Bot is running..."
uvicorn app:app --host 0.0.0.0 --port 8080
