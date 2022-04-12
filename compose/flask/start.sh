#!/bin/bash

python /app/check_conn.py --service-name db --port 5432  --ip db

alembic upgrade head

gunicorn 'app:create_app()' -b 0.0.0.0:8000


