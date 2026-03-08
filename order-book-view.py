
import time
import json
import requests
import logging
import argparse
from rich.console import Console
from rich.table import Table
from rich.live import Live


def parse_arguments():

    TIMEOUT_MIN = 2
    DEPTH_MIN = 1

    parser = argparse.ArgumentParser(description='Obtain an order book data from Binance')
    parser.add_argument('-s', '--symbol', type=str, default="BTCUSDT", metavar="name", help='instrument symbol (BTCUSDT,SOLUSDT,ETHUSDT,ETHBTC, ...)')
    parser.add_argument('-d', '--depth', type=int, default="15", metavar="number", help='number of price levels (default: 15)')
    parser.add_argument('-p', '--precision', type=int, default="2", metavar="number", help='floating point numbers precision (default : 2)')
    parser.add_argument('-t', '--timeout', type=int, default="3", metavar="number", help='update timeout in seconds (default: 3)')
    parser.add_argument('-H', '--host', type=str, metavar="URL", default="https://api.binance.com", help='host URL (default: https://api.binance.com )')

    args = parser.parse_args()

    args.timeout = max(args.timeout, TIMEOUT_MIN)
    args.depth = max(args.depth, DEPTH_MIN)

    return args
    
class OrderBook():

    ORDER_BOOK_REMOTE_REFERENCE_TEMPLATE:str = "{}/api/v3/depth?symbol={}&limit={}"	


    _remote_reference : str
    _symbol : str 
    _depth : int
    _bids : dict
    _asks : dict

    def __init__(self, host:str, symbol:str, depth:int):
        self._symbol = symbol
        self._depth = depth
        self._remote_reference = self.ORDER_BOOK_REMOTE_REFERENCE_TEMPLATE.format(host, symbol, depth)


    def refresh_content(self):
        result:bool = False
        js_data = self._load_order_book()
        if js_data:
           self._bids = dict(js_data.get("bids", None))
           self._asks = dict(js_data.get("asks", None))
           result = (self._bids and self._asks)
        return result        


    def get_symbol(self) -> str:
        return self._symbol
    
    def get_depth(self) -> int:
        return self._depth
    
    def get_asks(self) -> dict:
        return self._asks
    
    def get_bids(self) -> dict:
        return self._bids

    def _load_order_book(self): 
        result = requests.get(self._remote_reference)

        js_data = dict()
        if result.ok:
            js_data = json.loads(result.content.decode('utf-8')) 
        else:
            print(f"remote request failed: {result.status_code} ({result.reason})")
            if result.text:
               diagnosis = json.loads(str(result.text))
               print(f"response from server: {diagnosis.get('code', '')} ({diagnosis.get('msg', '')})") 
            exit()


        return js_data
    

class OrderBookRenderer():

    TITLE_TEMPLATE = "Order book for {} (depth {}, tm {}s)"

    _order_book:OrderBook
    _table:Table
    _timeout:int 

    def __init__(self, order_book:OrderBook, precision:int, timeout:int):
        self._order_book = order_book
        self._precision = precision
        self._timeout = timeout

    def render(self):
        print("Press Ctrl+C to quit ...\n")
        with Live(console=Console(), refresh_per_second=self._timeout) as live:
            while True:
                if self._order_book.refresh_content():
                    self._do_render(live)
                    time.sleep(self._timeout)
                else:
                    print("Cannot re-update content :-(")
                    break
            
    def _do_render(self, live):
        table = self._create_table()
        self._fill_table(table)
        live.update(table)
        
           
    def _create_table(self):
        title = self.TITLE_TEMPLATE.format(self._order_book.get_symbol(), self._order_book.get_depth(), self._timeout)
        table = Table(title=title)
        table.add_column("BID PRICE", justify="right")
        table.add_column("BID SIZE")
        table.add_column("ASK PRICE")
        table.add_column("ASK SIZE")
     
        return table

    def _fill_table(self, table:Table):
        if self._order_book.refresh_content():
            asks = self._order_book.get_asks()
            bids = self._order_book.get_bids()
            for (ask, aqt),  (bid, bqb) in zip(asks.items(), bids.items()):
                table.add_row(
                    str(round(float(bid), self._precision)),
                    str(round(float(bqb), self._precision)),
                    str(round(float(ask), self._precision)),
                    str(round(float(aqt), self._precision))
                )

if __name__ == "__main__":
    logging.basicConfig()

    args = parse_arguments()    

    order_book = OrderBook(args.host, args.symbol, args.depth)
    renderer = OrderBookRenderer(order_book, args.precision, args.timeout)
    renderer.render()
