#!/bin/bash

set -e

echo "Esperando a que PostgreSQL esté disponible..."
until python -c "import psycopg2; psycopg2.connect(host='db', port=5432, user='${POSTGRES_USER}', password='${POSTGRES_PASSWORD}', dbname='${POSTGRES_DB}')" 2>/dev/null; do
  echo "Esperando PostgreSQL..."
  sleep 1
done
echo "PostgreSQL está listo"

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "Iniciando servidor..."
exec "$@"
