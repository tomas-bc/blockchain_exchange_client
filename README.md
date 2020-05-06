# Sample Blockchain Exchange Client with simple bot

Python Client for Blockchain Exchange API (https://exchange.blockchain.com/api/#introduction).

You need [API keys] (https://exchange.blockchain.com/api/#to-get-started) for private functions of the API (trading).

Implemented features:

1. Subscribe to balances
    use `client.balances` for your latest balances
    
2. Subscribe to market data
    `client.prices` latest prices update
    `client.orderbook` latest orderbook updated snapshot
    `client.last_trade` last public trade
    
3. Subscribe to symbol reference data
    `client.symbols` reference infromation for exchange symbols

4. Create market, and limit orders
    
5. Get the state of an order
    client.orderStore keeps updated status on orders, examples to find status in client
    
6. Cancel an order

7. Cancel all orders
   
8. Create a bot that trades
    - simple momemtum bot with market trades implemented
    
    
How to use:
  1. Clone this repo
  2. Create Blockchain Exchange account and API keys
  3. Put your private API key in `client_manager.py` in line 33 
  4. Change your trading symbol and granuality in `client_manager.py` in lines 35-36 (defaults: 'BTC-USD' and 60 s)
  5. Select in `BCExClient.py` in `subscribe` what channels you want to subscribe (commenting out might affect funcionality of features and bot)
  6. Optional: Enable momentum trading bot by changing `trading_bot_trading_enabled` to `True`
  7. Run `client_manager.py`
  
Patterns for creating limit and market orders are implemented in the client.

Simple momentum strategy bot buys market when latest candle close is above last high and market sells when close below latest low.

Have fun trading!

  
    
    

