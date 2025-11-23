#!/bin/bash
# Setup script for initializing all databases

set -e

echo "Initializing Trading System Databases..."

# Create logs directory
mkdir -p logs

# Initialize Transactional Database
echo "Initializing Transactional Database..."
python src/database/transactional/manager.py

# Initialize Analytics Database
echo "Initializing Analytics Database..."
python src/database/analytics/aggregations.py

# Initialize Utilities Database
echo "Initializing Utilities Database..."
python src/database/utilities/model_params.py

# Initialize KDB+ (if running)
echo "Checking KDB+ connection..."
if command -v q &> /dev/null; then
    echo "KDB+ found. Loading schemas..."
    q src/database/historical/schemas.q -p 8080 &
    KDB_PID=$!
    sleep 2
    echo "KDB+ started with PID: $KDB_PID"
    echo "To stop KDB+: kill $KDB_PID"
else
    echo "KDB+ not found. Skipping KDB+ initialization."
    echo "Install KDB+ from https://kx.com/kdb-personal-edition-download/"
fi

echo ""
echo "Database initialization complete!"
echo ""
echo "Next steps:"
echo "1. Start RabbitMQ: brew services start rabbitmq"
echo "2. Start OBS: python main.py -s OBS"
echo "3. Start TES: python main.py -s TES"
echo "4. Start Trader Portal: python main.py --frontend trader"
