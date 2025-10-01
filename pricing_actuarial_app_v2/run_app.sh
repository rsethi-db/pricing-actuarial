#!/bin/bash

# Keep the app running and restart if it dies
while true; do
    echo "Starting app on port 8050..."
    python3 app.py
    echo "App died, restarting in 5 seconds..."
    sleep 5
done
