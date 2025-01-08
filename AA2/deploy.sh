#!/bin/bash

# Export LangSmith environment variables
export LANGCHAIN_API_KEY=your_langsmith_api_key
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_PROJECT="ga4-analytics-report"

# Run with production server
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
