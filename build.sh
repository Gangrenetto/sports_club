#!/usr/bin/env bash
# Сборка на Render: ставит пакеты, собирает CSS, создаёт базу и заполняет демо-данными.
set -o errexit   # остановиться при первой ошибке

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py seed_demo
