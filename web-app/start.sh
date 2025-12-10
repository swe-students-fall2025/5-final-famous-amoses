#!/bin/bash
# Startup script for Docker container
# Seeds the database, then starts the Flask app

set -e

echo "Seeding database..."
# The seed script already waits for MongoDB and handles errors
python -m database.seed || {
    echo "WARNING: Database seeding failed or database already seeded"
    # Continue anyway - database might already be seeded
}

echo "Starting Flask application..."
exec python run.py

