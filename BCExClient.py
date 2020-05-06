import json
from websocket import create_connection



class BlockchainExchangeClient:
    def __init__(self, api_key, symbol='BTC-USD', granuality=60):
        """

        :param api_key: your private key, don't commit to github or public repos
        :param symbol: symbol
        :param granuality: in seconds
        Blockchain Exchange API Documentation: https://exchange.blockchain.com/api/#websocket-api
        """
        self.api_key = api_key
        self.symbol = symbol
        self.granuality = granuality

        # Objects for status, orderbook and prices
        self.symbols = {}
        self.balances = {}
        self.last_trade = {}
        self.orderbook = {}
        self.prices = {}
        self.orderStore = {}
        self.sq = 0
        self.prev_low = 0
        self.prev_high = 0


        # Create conneciton
        options = {}
        options['origin'] = 'https://exchange.blockchain.com'
        url = "wss://ws.prod.blockchain.info/mercury-gateway/v1/ws"
        self.ws = create_connection(url, **options)

    def subscribe(self):
        # This handles subscription to channels, comment unwanted ones
        self.sub_authorize()
        self.sub_balances()
        self.sub_heartbeat()

        #self.sub_l3()
        self.sub_prices()
        self.sub_symbols()
        #self.sub_ticker()
        self.sub_trades()
        self.sub_trading()
        #self.sub_l2() # this one has to be last so that following snapshot gets caught in time
        return

    def sub_authorize(self):
        msg = json.dumps({"token": f"{self.api_key}", "action": "subscribe", "channel": "auth"})
        self.ws.send(msg)
        print(self.ws.recv())
        return

    def sub_heartbeat(self):
        msg = '{"action": "subscribe", "channel": "heartbeat"}'
        self.ws.send(msg)
        print(self.ws.recv())
        return
    def sub_balances(self):
        msg = '{"action": "subscribe", "channel": "balances"}'
        self.ws.send(msg)
        print(self.ws.recv())
        return
    def sub_l2(self):
        msg = json.dumps({"action": "subscribe", "channel": "l2", "symbol": self.symbol})
        self.ws.send(msg)
        print(self.ws.recv())
        return
    def sub_l3(self):
        msg = json.dumps({"action": "subscribe", "channel": "l3", "symbol": self.symbol})
        self.ws.send(msg)
        print(self.ws.recv())
        return
    def sub_ticker(self):
        msg = json.dumps({"action": "subscribe", "channel": "ticker", "symbol": self.symbol})
        self.ws.send(msg)
        print(self.ws.recv())
        return
    def sub_symbols(self):
        msg = '{"action": "subscribe", "channel": "symbols"}'
        self.ws.send(msg)
        print(self.ws.recv())
        return
    def sub_prices(self):
        msg = json.dumps({"action": "subscribe", "channel": "prices", "symbol": self.symbol, "granularity": self.granuality})
        self.ws.send(msg)
        print(self.ws.recv())
        return
    def sub_trades(self):
        msg = json.dumps({"action": "subscribe", "channel": "trades", "symbol": self.symbol})
        self.ws.send(msg)
        print(self.ws.recv())
        return
    def sub_trading(self):
        msg = json.dumps({"action": "subscribe", "channel": "trading"})
        self.ws.send(msg)
        print(self.ws.recv())
        return

    def create_order(self, pair, price, quantity, side, type):
        my_reference = 'TUCTUC'  # this is your order id reference to identify your orders

        if type == 'limit':
            order = {
                "action": 'NewOrderSingle',
                'channel': 'trading',
                'clOrdID': my_reference,
                'symbol': pair,
                'ordType': type,
                'timeInForce': 'GTC',
                'side': side,
                'orderQty': quantity,
                'price': price,
                # 'stopPx': stopPx,
                'execInst': "ALO"

            }

        elif type == 'market':
            order = {
                "action": 'NewOrderSingle',
                'channel': 'trading',
                'clOrdID': my_reference,
                'symbol': pair,
                'ordType': type,
                'timeInForce': 'GTC',
                'side': side,
                'orderQty': quantity,
                'price': price,
                # 'stopPx': stopPx,
                'execInst': "ALO"

            }

        else:
            print(f'Order type {type} not supported in this template')

        return json.dumps(order)

    def cancel_order(self, order_id):
        return json.dumps({
            "action": "CancelOrderRequest",
            "channel": "trading",
            "orderID": order_id,
        })

    def cancel_all_open_orders(self):
        for orderID in self.orderStore.keys():
            if self.orderStore[orderID]['ordStatus'] == 'open':
                msg = self.cancel_order(orderID)
                self.ws.send(msg)
                print(f'Cancelling opened order with ID {orderID} full order details: {self.orderStore[orderID]} ')

    def msg_handler(self, message):
        """
        This method parses a update message and updates status of your orders, keeps latest orderbook and latest public trade
        """
        message = json.loads(message)
        print(message)
        self.sq += 1

        # symbols status
        if message['channel'] == 'symbols' and message['event'] == 'snapshot': self.symbols = message['symbols']
        if message['channel'] == 'symbols' and message['event'] == 'updated':
            self.symbol = message['symbol']
            for key_update in message.keys():
                if key_update in self.symbols.keys():
                    self.symbols[self.symbol]['key_update'] = message['key_update']

            print(f'Updated status for symbols object : {self.symbols}')

        # balances status
        if message['channel'] == 'balances' and message['event'] == 'snapshot':
            self.balances = message['balances']
            print(f'Balances were updated: {self.balances}')

        # trade public
        if message['channel'] == 'trades' and message['event'] == 'updated':
            self.last_trade = message
            print(f'Last public trade: {self.last_trade}')

        # prices status
        if message['channel'] == 'prices' and message['event'] == 'updated':
            self.prices = message['price']
            print(f'prices updated')
            self.trading_bot()

        # Orderbook - Algorithm to keep orderbook up to date
        if message['channel'] == 'l2' and message['event'] == 'snapshot':
            self.orderbook = message
            print(f'Orderbook snapshot received: {self.orderbook}')
        if message['channel'] == 'l2' and message['event'] == 'updated':
            #print(f'Received orderbook update {message}')
            if len(message['bids']) > 0:
                for update in message['bids']:
                    d = []
                    for i, level in enumerate(self.orderbook['bids']):
                        if level['px'] == update['px']:
                            if update['qty'] != 0.0:
                                self.orderbook['bids'][i] = update  # update level
                            else:
                                d.append(i)  # add to delete levels list
                            break
                    if len(d) != 0:  # delete levels
                        for _ in d: del self.orderbook['bids'][_]

            if len(message['asks']) > 0:
                for update in message['asks']:
                    d = []
                    for i, level in enumerate(self.orderbook['asks']):
                        if level['px'] == update['px']:
                            if update['qty'] != 0:
                                self.orderbook['asks'][i] = update  # update level
                            else:
                                d.append(i)  # add to delete levels list
                            break
                    if len(d) != 0:  # delete levels
                        for _ in d: del self.orderbook['asks'][_]
            print(f'orderbook after update {self.orderbook}')

        # Trading Private
        if message['channel'] == 'trading':
            print(message)
            print()
            if message['event'] == 'snapshot' and len(message['orders']) > 0:
                for order in message['orders']:
                    self.orderStore[order['orderID']] = order
                print(f'Order Store Updated {self.orderStore}')
                print()

            if message['event'] == 'updated':
                self.orderStore[message['orderID']] = message

    def trading_bot(self):
        """
        Simple momentum based bot that makes market trade based on candlestick moves

        If close of current candle is higher then high of previous --> buy
        if close of current candle is lower then low of previous --> sell

        This is just an example, dont get reckt!

        For simplicity this would trade small amount and assume availble balances
        """

        if self.prices[4] > self.prev_high:
            print(f'Buying Market: close higher then last high for candle {self.prices} with last {self.prev_high}')
            if self.trading_bot_trading_enabled == True and self.prev_low != 0 or self.prev_high != 0:
                # Create order at last close to buy
                order = self.create_order(self.symbol,self.prices[4],0.0001,'buy',type='market')
                print(f'Order Sent: {order}')

        elif self.prices[4] < self.prev_low:
            print(f'Selling Market: close lower then last low for candle {self.prices} with last {self.prev_low}')
            if self.trading_bot_trading_enabled == True and self.prev_low != 0 or self.prev_high != 0:
                # Create order at last close to sell
                order = self.create_order(self.symbol, self.prices[4], 0.0001, 'sell', type='market')
                print(f'Order Sent: {order}')

        self.prev_high = self.prices[2]
        self.prev_low = self.prices[3]
        print(f'updated last candle, {self.prev_high} {self.prev_low} ')


