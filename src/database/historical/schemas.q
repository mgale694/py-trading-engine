/ KDB+ Schema Definitions for Historical Data
/ Run this script in your q session to initialize tables

/ Trade table - stores executed trades
trade:([] 
    id:`symbol$(); 
    timestamp:`timestamp$(); 
    symbol:`symbol$(); 
    quantity:`float$(); 
    price:`float$();
    buyer:`symbol$();
    seller:`symbol$()
)

/ Quote table - stores market quotes (bid/ask)
quote:([] 
    timestamp:`timestamp$(); 
    symbol:`symbol$(); 
    bid:`float$(); 
    ask:`float$(); 
    bid_size:`float$(); 
    ask_size:`float$()
)

/ Order book snapshot table
orderbook_snapshot:([] 
    timestamp:`timestamp$(); 
    symbol:`symbol$(); 
    level:`int$(); 
    bid_price:`float$(); 
    bid_size:`float$(); 
    ask_price:`float$(); 
    ask_size:`float$()
)

/ Market depth table
market_depth:([] 
    timestamp:`timestamp$(); 
    symbol:`symbol$(); 
    side:`symbol$(); 
    price:`float$(); 
    size:`float$(); 
    order_count:`int$()
)

/ Display confirmation
show "Historical database tables created successfully"
show tables[]
