import time
import pykx as kx


class BasicStrategy:
    """
    A basic order matching strategy that can be extended for more advanced logic.
    For now, this will simply provide a placeholder for matching logic.
    """

    def __init__(self):
        print("BasicStrategy initialised.")
        # Set up kdb+ connection using pykx
        self.q = kx.QConnection(host='localhost', port=8080)

    def match_orders(self, bids, asks):
        """
        Match orders using a simple price-time priority.
        Returns a list of matched trades, each with id and timestamp.
        """
        trades = []
        trade_id = 1
        while bids and asks and bids[0]["price"] >= asks[0]["price"]:
            bid = bids[0]
            ask = asks[0]
            trade_qty = min(bid["quantity"], ask["quantity"])
            trade_price = ask["price"]
            trade = {
                "id": trade_id,
                "timestamp": time.time(),
                "buyer": bid["user_id"],
                "seller": ask["user_id"],
                "quantity": trade_qty,
                "price": trade_price,
            }
            trades.append(trade)
            trade_id += 1
            bid["quantity"] -= trade_qty
            ask["quantity"] -= trade_qty
            if bid["quantity"] == 0:
                bids.pop(0)
            if ask["quantity"] == 0:
                asks.pop(0)
        return trades

    def run(self, order_context):
        """
        Accept the order context and return a result.
        This allows the server to call the strategy with the order context.
        """
        print(f"Strategy running with context: {order_context}")
        # Record the trade in kdb+ using pykx
        try:
            # Use a dict of lists for each column, even for a single row
            trade_table = kx.Table(data={
                'id': [str(order_context['id'])],
                'timestamp': [order_context['timestamp']],
                'symbol': [str(order_context.get('symbol', ''))],
                'quantity': [order_context.get('quantity', 0)],
                'price': [order_context.get('price', 0)]
            })
            self.q('insert', 'trade', trade_table)
        except Exception as e:
            print(f"Failed to insert trade into kdb+: {e}")
        # Always return a JSON-serializable response and flush stdout
        return {"status": "processed", "order_id": order_context["id"]}
