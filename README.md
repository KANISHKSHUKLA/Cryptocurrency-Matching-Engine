# Cryptocurrency Matching Engine

A high-performance cryptocurrency matching engine built with Python and FastAPI. This project implements a real-time order matching system that supports various order types and provides WebSocket-based market data and trade updates.

## Features

- **Multiple Order Types Support**:
  - Limit Orders
  - Market Orders
  - Immediate-or-Cancel (IOC) Orders
  - Fill-or-Kill (FOK) Orders

- **Real-time Market Data**:
  - WebSocket-based market data streaming
  - Best Bid and Offer (BBO) updates
  - Order book depth updates
  - Real-time trade execution notifications

- **REST API Endpoints**:
  - Order submission
  - Order cancellation
  - Market data queries

- **Price-Time Priority**:
  - Orders are matched based on price and time priority
  - First-in-first-out (FIFO) matching within price levels

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cryptocurrency-matching-engine
```

2. Create a virtual environment (recommended):
```bash
py -3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
cryptocurrency-matching-engine/
├── matching_engine/
│   ├── __init__.py
│   ├── engine.py      # Core matching engine implementation
│   └── api.py         # FastAPI endpoints and WebSocket handlers
├── tests/
│   └── test_engine.py # Unit tests
├── websocket_client.py # Example WebSocket client
├── main.py            # Application entry point
└── requirements.txt   # Project dependencies
```

## Usage

### Starting the Server

Run the matching engine server:
```bash
python main.py
```

The server will start on `http://localhost:8000`.

### REST API Endpoints

1. **Submit an Order**
```bash
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USDT",
    "order_type": "limit",
    "side": "buy",
    "quantity": "1.0",
    "price": "50000.0"
  }'
```

2. **Cancel an Order**
```bash
curl -X DELETE http://localhost:8000/order/BTC-USDT/{order_id}
```

3. **Get Best Bid and Offer**
```bash
curl http://localhost:8000/bbo/BTC-USDT
```

### WebSocket Connections

The engine provides two WebSocket endpoints for real-time updates:

1. **Market Data WebSocket**
```python
import asyncio
import websockets
import json

async def connect_market_data():
    uri = "ws://localhost:8000/ws/market-data"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print("Market Data:", json.loads(data))

asyncio.run(connect_market_data())
```

2. **Trades WebSocket**
```python
import asyncio
import websockets
import json

async def connect_trades():
    uri = "ws://localhost:8000/ws/trades"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print("Trade:", json.loads(data))

asyncio.run(connect_trades())
```

## Real-World Usage Scenario

Let's walk through a practical example of how to use the matching engine in a real-world trading scenario.

### Step 1: Setup and Monitoring

1. Start the matching engine server:
```bash
python main.py
```

2. In a separate terminal, start the WebSocket client to monitor market data and trades:
```bash
python websocket_client.py
```

### Step 2: Market Making Scenario

Let's simulate a market maker providing liquidity for BTC-USDT:

1. **Initial Market Making Orders**
```bash
# Place a limit buy order at $49,000
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USDT",
    "order_type": "limit",
    "side": "buy",
    "quantity": "2.0",
    "price": "49000.0"
  }'

# Place a limit sell order at $51,000
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USDT",
    "order_type": "limit",
    "side": "sell",
    "quantity": "2.0",
    "price": "51000.0"
  }'
```

2. **Check the Order Book**
```bash
curl http://localhost:8000/bbo/BTC-USDT
```
You should see the best bid at $49,000 and best ask at $51,000.

### Step 3: Trading Scenario

Now let's simulate some trading activity:

1. **Market Order Execution**
```bash
# Place a market buy order for 1.5 BTC
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USDT",
    "order_type": "market",
    "side": "buy",
    "quantity": "1.5"
  }'
```
This will execute against the limit sell order at $51,000.

2. **Limit Order with Price Improvement**
```bash
# Place a limit buy order at $50,500
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USDT",
    "order_type": "limit",
    "side": "buy",
    "quantity": "1.0",
    "price": "50500.0"
  }'
```

### Step 4: Order Management

1. **Cancel an Order**
```bash
# Cancel the remaining limit sell order
curl -X DELETE http://localhost:8000/order/BTC-USDT/{order_id}
```

2. **Place New Orders**
```bash
# Place a new limit sell order at $52,000
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USDT",
    "order_type": "limit",
    "side": "sell",
    "quantity": "1.0",
    "price": "52000.0"
  }'
```

### Step 5: Advanced Order Types

1. **Immediate-or-Cancel (IOC) Order**
```bash
# Place an IOC buy order
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USDT",
    "order_type": "ioc",
    "side": "buy",
    "quantity": "2.0",
    "price": "51500.0"
  }'
```

2. **Fill-or-Kill (FOK) Order**
```bash
# Place a FOK sell order
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USDT",
    "order_type": "fok",
    "side": "sell",
    "quantity": "3.0",
    "price": "51000.0"
  }'
```

### Step 6: Monitoring and Analysis

Throughout the trading session, you can monitor:
- Real-time market data through the WebSocket connection
- Trade executions and their details
- Order book depth and liquidity
- Best bid and offer prices

The WebSocket client will show you:
- Market data updates including order book changes
- Trade executions with prices and quantities
- Real-time updates of the order book state


## If you want to use PostMan or other application to test the APIs 
    here's the step by step demo for that->

## Setup
1. Open Postman
2. Create a new environment:
   - Name: "Trading Demo"
   - Variable: `base_url` = http://localhost:8000
3. Open two WebSocket connections in Postman:
   - Market Data: `ws://localhost:8000/ws/market-data`
   - Trades: `ws://localhost:8000/ws/trades`

## Demo Flow

### 1. Understanding the Order Book
"Let me explain how an order book works:
- The order book is like a marketplace where buyers and sellers meet
- Buyers place 'bids' (the prices they're willing to buy at)
- Sellers place 'asks' (the prices they're willing to sell at)
- The best bid is the highest price a buyer is willing to pay
- The best ask is the lowest price a seller is willing to accept"

### 2. Initial Market State
"Let's check the current market state:"
- GET `http://localhost:8000/bbo/BTC-USDT`
- Expected Response:
```json
{
    "symbol": "BTC-USDT",
    "best_bid": null,
    "best_ask": null
}
```
"Notice that both best bid and best ask are null because there are no orders in the market yet."

### 3. Building the Order Book
"Let's start building our order book with some limit orders:"

#### 3.1 Place First Buy Order
"First, let's place a buy order at $50,000:"
- POST `http://localhost:8000/order`
- Body:
```json
{
    "symbol": "BTC-USDT",
    "order_type": "limit",
    "side": "buy",
    "quantity": "1.0",
    "price": "50000.0"
}
```
- Expected Response:
```json
{
    "order_id": "uuid-string",
    "status": "accepted",
    "executions": []
}
```
"Notice in the WebSocket market data stream that we now have a bid at $50,000."

#### 3.2 Place Second Buy Order
"Let's place another buy order at a lower price:"
- POST `http://localhost:8000/order`
- Body:
```json
{
    "symbol": "BTC-USDT",
    "order_type": "limit",
    "side": "buy",
    "quantity": "0.5",
    "price": "49000.0"
}
```
"Now we have two buy orders in our order book, creating depth on the buy side."

#### 3.3 Place First Sell Order
"Now, let's place a sell order:"
- POST `http://localhost:8000/order`
- Body:
```json
{
    "symbol": "BTC-USDT",
    "order_type": "limit",
    "side": "sell",
    "quantity": "0.8",
    "price": "51000.0"
}
```
"Notice how the order book now shows both buy and sell orders."

### 4. Check Order Book State
"Let's check our current order book state:"
- GET `http://localhost:8000/bbo/BTC-USDT`
- Expected Response:
```json
{
    "symbol": "BTC-USDT",
    "best_bid": "50000.0",
    "best_ask": "51000.0"
}
```
"Here we can see:
- The best bid is $50,000 (highest price a buyer is willing to pay)
- The best ask is $51,000 (lowest price a seller is willing to accept)
- The difference between these prices is called the 'spread'"

### 5. Demonstrate Order Matching
"Now, let's see how orders match when prices cross:"

#### 5.1 Place Matching Sell Order
"Let's place a sell order that will match with our highest bid:"
- POST `http://localhost:8000/order`
- Body:
```json
{
    "symbol": "BTC-USDT",
    "order_type": "limit",
    "side": "sell",
    "quantity": "0.3",
    "price": "50000.0"
}
```
"Watch the trades WebSocket - you should see a trade execution!"

### 6. Market Order Demonstration
"Let's demonstrate how market orders work:"
- POST `http://localhost:8000/order`
- Body:
```json
{
    "symbol": "BTC-USDT",
    "order_type": "market",
    "side": "buy",
    "quantity": "0.2"
}
```
"Market orders execute immediately at the best available price. Notice how it matches with the lowest ask in our order book."

### 7. Order Cancellation
"Let's demonstrate order cancellation:"
- DELETE `http://localhost:8000/order/BTC-USDT/{order_id}`
"Notice how the order book updates in the WebSocket stream when we cancel an order."

### 8. Real-time Updates
"Throughout this demo, you can see:
1. Market Data WebSocket shows:
   - Order book updates
   - Price changes
   - Order book depth
2. Trades WebSocket shows:
   - Executed trades
   - Trade prices
   - Trade quantities"

## Key Concepts Demonstrated
1. **Order Book Structure**
   - Bids (buy orders)
   - Asks (sell orders)
   - Price-time priority

2. **Order Types**
   - Limit orders (specified price)
   - Market orders (immediate execution)

3. **Price Discovery**
   - Best bid and offer
   - Spread calculation
   - Market depth

4. **Real-time Updates**
   - Order book changes
   - Trade executions
   - Market data streaming


## Conclusion
"This demo has shown how a real trading system:
- Maintains an order book
- Matches buy and sell orders
- Provides real-time market data
- Executes trades efficiently
- Manages order lifecycle"



## Testing

Run the test suite:
```bash
pytest tests/
```

The test suite includes comprehensive tests for:
- Limit order matching
- Market order matching
- IOC and FOK order handling
- Price-time priority
- Order cancellation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 