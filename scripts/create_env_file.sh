#!/bin/bash
# Create .env file for CI/Docker
echo "DEBUG=False" > .env
echo "SECRET_KEY=${SECRET_KEY}" >> .env
echo "ALLOWED_HOSTS=*" >> .env
echo "DATABASE_URL=${DATABASE_URL}" >> .env
