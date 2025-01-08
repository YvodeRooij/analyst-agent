#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Load environment variables from .env
if [ -f .env ]; then
    echo "Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Error: .env file not found"
    exit 1
fi

# Verify required environment variables
required_vars=(
    "LANGCHAIN_API_KEY"
    "GA_PROPERTY_ID"
    "GA_REFRESH_TOKEN"
    "GA_CLIENT_ID"
    "GA_CLIENT_SECRET"
    "EMAIL_USERNAME"
    "EMAIL_PASSWORD"
    "FROM_EMAIL"
    "GESPREKSEIGENAAR_EMAIL"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set in .env file"
        exit 1
    fi
done

# Export LangSmith environment variables
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_PROJECT="ga4-analytics-report"

echo "Starting server..."
# Run with production server
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
