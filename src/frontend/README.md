# Frontend Applications

This directory contains all user-facing applications.

## Structure

```
frontend/
├── trader-portal/      # External trader interface
│   ├── app.py         # Main Streamlit app
│   ├── pages/         # Multi-page sections
│   ├── components/    # Reusable UI components
│   └── utils/         # Frontend utilities
│
└── analytics/          # Internal analytics dashboard
    ├── app.py         # Main dashboard app
    ├── pages/         # Dashboard sections
    └── components/    # Visualization components
```

## Trader Portal

**Purpose:** External-facing application for traders to:

- Place and manage orders
- View positions and portfolios
- Track P&L
- Access basic analytics

**Technology:** Streamlit (rapid prototyping), planned migration to React

### Running Trader Portal

```bash
streamlit run src/frontend/trader-portal/app.py
```

### Features

- 📊 **Dashboard**: Overview of account and recent activity
- 📝 **Order Entry**: Place market and limit orders
- 💼 **Positions**: View current positions and P&L
- 📈 **Analytics**: Basic performance metrics and charts

## Analytics Dashboard

**Purpose:** Internal dashboard for system operators to:

- Monitor system health
- Track performance metrics
- Analyze user activity
- View operational statistics

**Technology:** Streamlit with Plotly for visualizations

### Running Analytics Dashboard

```bash
streamlit run src/frontend/analytics/app.py
```

### Features

- 🏥 **System Health**: Server status and health checks
- 📈 **Performance Metrics**: Trading volume, execution quality
- 👥 **User Activity**: User statistics and behavior
- 🔍 **System Insights**: Operational analytics

## Database Connectivity

Both frontends connect to the appropriate databases:

**Trader Portal:**

- Transactional DB (read/write orders, positions)
- Analytics DB (read performance metrics)

**Analytics Dashboard:**

- All databases (read-only for monitoring)

## Configuration

Create `.streamlit/config.toml` for custom styling:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
address = "localhost"
```

## Future Enhancements

- [ ] **Trader Portal**: Migrate to React + FastAPI backend
- [ ] **Real-time Updates**: WebSocket integration for live data
- [ ] **Authentication**: JWT-based user authentication
- [ ] **Mobile Responsive**: Optimize for mobile devices
- [ ] **Advanced Charts**: TradingView integration
- [ ] **Alerts**: Real-time notifications and alerts
- [ ] **Dark Mode**: Theme switcher
