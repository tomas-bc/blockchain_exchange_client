import BCExClient

'''
Objectives:

1. Subscribe to balances
    in: client.balances
    
2. Subscribe to market data
    client.prices
    client.orderbook
    client.last_trade
    
3. Subscribe to symbol reference data
    in: client.symbols

Create market, and limit orders
    patterns in client, used by bot or commented code below
    
Get the state of an order
    client.orderStore keeps updated status on orders, examples to find status in client
    
Cancel an order
    implemented
Cancel all orders
    implemented

Create a bot that trades
    simple momemtum bot with market trades implemented
'''

# PUT YOUR API SECRET HERE - BE AWARE OF SECURITY, NEVER DISCLOSE PUBLICLY
API_SECRET = ""

symbol = 'BTC-USD'
granuality = 60
client = BCExClient.BlockchainExchangeClient(API_SECRET, symbol=symbol, granuality=granuality)

client.subscribe()
client.trading_bot_trading_enabled = False  # enables trading bot to place orders


while True:

    message = client.ws.recv()
    client.msg_handler(message)



    #if client.sq == 10: # Do something on messge number X from websocket (e.g. need to wait little bit to receive open orders snapshot to cancell them all)

    # Cancel ALl Opened Orders
    #client.cancel_all_open_orders()

    # Send order
    # client.ws.send(client.create_order(pair = 'BTC-GBP', price = 1000, quantity = 0.001, side = 'buy', type = 'limit'))
    # result = client.ws.recv()
    # print(f'Snapshot of live orders {result}')

    # Cancel Order
    # client.ws.send(cancel_order(168243914241)) #put your order ID here
    # result = client.ws.recv()
    # print(f' Cancel response {result}')