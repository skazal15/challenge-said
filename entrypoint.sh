#!/bin/bash
set -e

if [ "$SKIP_DB_SETUP" = "true" ]; then
  echo "Skipping DynamoDB setup..."
  exec "$@"
fi

echo "Waiting for DynamoDB Local to be ready..."
until curl -s http://dynamodb-local:8000 > /dev/null; do
  echo "DynamoDB is unavailable - sleeping"
  sleep 2
done

echo "DynamoDB Local is up! Ensuring BooksTable exists..."
aws dynamodb create-table \
    --table-name BooksTable \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url http://dynamodb-local:8000 \
    --region us-east-1 || echo "Table already exists."

exec "$@"
