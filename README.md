# py-trading-engine

A modular Python trading engine designed for real-time trading, order management, and analytics. This project is structured for extensibility and clarity, with a Streamlit-based frontend, a robust backend trading engine, and a flexible database layer.

## Project Structure

- **src/frontend/**: Streamlit-based user interface for traders to interact with the system.
- **src/backend/**: Core trading engine logic, including order matching, orderbook management, and PnL calculations.
- **src/database/**: Database integration for storing trades, user data, and market data.

## Features

- **User Authentication**: Traders can securely log in to the platform.
- **Order Placement**: Place buy/sell orders through the frontend, which are routed to the backend engine.
- **Orderbook Management**: Real-time orderbook with summary, volume, and order matching logic.
- **Trade Matching**: Engine matches orders and executes trades according to market rules.
- **PnL Overview**: Real-time profit and loss breakdown for each trader and the overall system.
- **Database Storage**: All trades, orders, and user data are stored in a database for persistence and analytics.

## Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/) for rapid UI development and real-time updates.
- **Backend**: Python-based trading engine with modular components for order management, matching, and analytics.
- **Database**:
  - *Market Data*: (Recommended) [kdb+](https://kx.com/) for high-performance, real-time ticker data storage and retrieval.
  - *Trade & User Data*: Alternatives such as PostgreSQL, SQLite, or MongoDB can be used for storing trades, orders, and user information.

## Getting Started

1. **Clone the repository**
   ```sh
   git clone https://github.com/yourusername/py-trading-engine.git
   cd py-trading-engine
   ```
2. **Install dependencies**
   - Backend and frontend Python dependencies (see `requirements.txt`)
   - Database setup as per your chosen backend
3. **Run the frontend**
   ```sh
   streamlit run src/frontend/app.py
   ```
4. **Run the backend**
   ```sh
   python src/backend/main.py
   ```

## Contributing

Contributions are welcome! Please open issues or submit pull requests for new features, bug fixes, or improvements.

## License

This project is licensed under the MIT License.