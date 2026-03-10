#!/bin/bash

# Script to build and run the Docker containers for the camera scanner
set -e

echo "=== Building the Docker containers ==="
docker compose build

echo "=== Verifying OpenCV installation in the container ==="
docker compose run --rm camera_scanner python check_opencv.py

if [ $? -eq 0 ]; then
    echo "=== OpenCV is working correctly ==="
    echo "=== Starting all containers ==="
    docker compose up -d
    
    echo "=== Checking container logs ==="
    docker compose logs -f
else
    echo "=== ERROR: OpenCV check failed ==="
    echo "Try to fix the issue manually. You might need to update the requirements.txt file."
    exit 1
fi 