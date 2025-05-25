#!/bin/bash
# Script to run the CRM system

# Activate virtual environment if it exists (optional but recommended)
# if [ -d "venv" ]; then
#   source venv/bin/activate
# fi

# Initialize database if it doesn't exist
if [ ! -f "database/crm.db" ]; then
  echo "Initializing database..."
  flask db init
  flask db migrate -m "Initial migration."
  flask db upgrade
  flask init-db
  echo "Database initialized."
fi

# Run the Flask application
echo "Starting CRM system on http://127.0.0.1:5000"
flask run --host=0.0.0.0 --port=5000
