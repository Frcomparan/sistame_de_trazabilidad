#!/bin/bash

set -e

echo "Esperando a que PostgreSQL esté disponible..."
until python -c "import psycopg2; psycopg2.connect(host='db', port=5432, user='${POSTGRES_USER}', password='${POSTGRES_PASSWORD}', dbname='${POSTGRES_DB}')" 2>/dev/null; do
  echo "Esperando PostgreSQL..."
  sleep 1
done
echo "PostgreSQL está listo"

# Skip migrations if migrations don't exist yet
if [ -f "/app/apps/core/migrations/0001_initial.py" ]; then
    echo "Aplicando migraciones..."
    python manage.py migrate --noinput

    echo "Recolectando archivos estáticos..."
    python manage.py collectstatic --noinput --clear
fi

echo "Iniciando servidor..."
exec "$@"
