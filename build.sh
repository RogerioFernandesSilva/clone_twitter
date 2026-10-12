#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
# Para popular dados fictícios no deploy, defina SEED=1 nas variáveis de ambiente
if [ "$SEED" = "1" ]; then python manage.py seed; fi
