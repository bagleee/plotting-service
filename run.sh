#!/bin/bash

mkdir -p db_data

sudo docker build -t demo-server-project .
sudo docker run --rm \
    -p 8501:8501 \
    -v "$(pwd)/db_data:/app/db_data" \
    -e DATABASE_PATH="/app/db_data/users.db" \
    --name demo-server \
    demo-server-project