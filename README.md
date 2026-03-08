# $\color{MidnightBlue}\textit{\textbf{order-book-view}}$

![Python](https://img.shields.io/badge/Python-v%203.x-lightblue?logo=python) 


Python app that visualizes Binance Order Book data.


#### What the app does:
 Internally, the app utilizes REST API to fetch Order Book data 
 from Binance service and displays it in a terminal


#### Command line arguments:
        
```
-h, --help      show this help message and exit
-s, --symbol    instrument symbol (BTCUSDT,SOLUSDT,ETHUSDT,ETHBTC, ...) (BTCUSDT by default)
-d, --depth     number of price levels (15 by default)
-p, --precision floating point numbers precision (2 by default)
-t, --timeout   update timeout (3s by default)
-H, --host      host URL (default: https://api.binance.com)

```
#### Samples of usage:

```
python order-book-view.py --symbol=SOLUSDT
python order-book-view.py --symbol=ETHUSDT --depth 20
python order-book-view.py --symbol=BTCUSDT --depth 15 --timeout 5
python order-book-view.py --symbol=BTCUSDT --depth 20 --precision 2
```

#### Screenshots:
-----------------
<img src="screenshots/Screenshot.01.png" width="400" high="600">