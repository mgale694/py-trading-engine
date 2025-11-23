#!/bin/bash
# Complete development setup script
# Initializes databases and loads mock data

set -e

echo "=========================================="
echo "Trading System - Development Setup"
echo "=========================================="
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Set environment to dev
export ENV=dev

echo "Step 1: Creating logs directory..."
mkdir -p logs

echo ""
echo "Step 2: Initializing databases..."
echo "  - Transactional database"
python -c "from src.database.transactional.manager import init_db; init_db()"

echo "  - Analytics database"
python -c "from src.database.analytics.aggregations import init_analytics_db; init_analytics_db()"

echo "  - Utilities database"
python -c "from src.database.utilities.model_params import init_utilities_db; init_utilities_db()"

echo ""
echo "Step 3: Loading mock data..."
python main.py --init-mock-data

echo ""
echo "Step 4: Checking RabbitMQ..."
if command -v rabbitmqctl &> /dev/null; then
    if rabbitmqctl status &> /dev/null; then
        echo "  ✅ RabbitMQ is running"
    else
        echo "  ⚠️  RabbitMQ is not running. Starting..."
        if command -v brew &> /dev/null; then
            brew services start rabbitmq
            sleep 3
            echo "  ✅ RabbitMQ started"
        else
            echo "  ⚠️  Please start RabbitMQ manually"
        fi
    fi
else
    echo "  ⚠️  RabbitMQ not found. Please install RabbitMQ:"
    echo "     brew install rabbitmq"
fi

echo ""
echo "Step 5: Checking KDB+ (optional)..."
if command -v q &> /dev/null; then
    echo "  ✅ KDB+ found"
    echo "  To start KDB+: q src/database/historical/schemas.q -p 8080"
else
    echo "  ℹ️  KDB+ not found (optional)"
    echo "     Install from: https://kx.com/kdb-personal-edition-download/"
fi

echo ""
echo "=========================================="
echo "✅ Development Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the Order Book Server (Terminal 1):"
echo "   python main.py -s OBS"
echo ""
echo "2. Start the Trading Engine Server (Terminal 2):"
echo "   python main.py -s TES"
echo ""
echo "3. Choose one of the following:"
echo ""
echo "   Option A: Start simulated traders (Terminal 3):"
echo "   python main.py --simulated-traders 5"
echo ""
echo "   Option B: Start a manual trader client (Terminal 3):"
echo "   python main.py -c trader"
echo ""
echo "   Option C: Start the Trader Portal (Terminal 3):"
echo "   python main.py --frontend trader"
echo ""
echo "4. (Optional) View Analytics Dashboard (Terminal 4):"
echo "   python main.py --frontend analytics"
echo ""
echo "=========================================="
echo ""
echo "Configuration:"
echo "  - Environment: dev"
echo "  - Config file: config/dev.yaml"
echo "  - Databases:"
echo "    • Transactional: src/database/transactional/trading_engine.db"
echo "    • Analytics: src/database/analytics/analytics.db"
echo "    • Utilities: src/database/utilities/utilities.db"
echo "  - RabbitMQ: localhost:5672"
echo "  - Management UI: http://localhost:15672 (guest/guest)"
echo ""
echo "Mock Data Loaded:"
echo "  - 20 users"
echo "  - 100 orders"
echo "  - 50 trades"
echo "  - 10 instruments (AAPL, GOOGL, MSFT, TSLA, AMZN, etc.)"
echo ""
echo "=========================================="
