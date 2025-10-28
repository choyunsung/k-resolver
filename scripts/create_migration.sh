#!/bin/bash
# Create a new Alembic migration

if [ -z "$1" ]; then
    echo "Usage: $0 <migration_message>"
    echo "Example: $0 'add user table'"
    exit 1
fi

echo "Creating migration: $1"
alembic revision --autogenerate -m "$1"
