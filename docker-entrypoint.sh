#!/bin/bash
set -e

echo "Waiting for MySQL to be ready..."

# Wait for MySQL using Python connection attempt
until python3 << END
import sys
import mysql.connector
try:
    conn = mysql.connector.connect(
        host="${DB_HOST}",
        user="${DB_USER}",
        password="${DB_PASSWORD}",
        database="${DB_NAME}"
    )
    conn.close()
    sys.exit(0)
except Exception as e:
    sys.exit(1)
END
do
    echo "Waiting for database connection..."
    sleep 2
done

echo "MySQL is ready!"

# Check if database should be seeded (only on first run or if flag is set)
if [ "${SEED_DATABASE:-true}" = "true" ]; then
    echo "Seeding database with test data..."
    python3 /app/seed_data.py
    
    if [ $? -eq 0 ]; then
        echo "Database seeded successfully!"
    else
        echo "Warning: Database seeding failed, but continuing..."
    fi
else
    echo "Skipping database seeding (SEED_DATABASE=false)"
fi

echo "Starting Flask application..."
# Execute the main command
exec "$@"
